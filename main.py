"""
Main Application - Smart Traffic Light Monitoring System
Integrates all components for real-time traffic monitoring and signal control
"""

import cv2
import numpy as np
import argparse
import logging
import time
import yaml
from pathlib import Path

from src.vehicle_detector import VehicleDetector
from src.traffic_analyzer import TrafficAnalyzer
from src.signal_controller import SignalController


class TrafficMonitoringSystem:
    """
    Main system integrating detection, analysis, and signal control
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize the traffic monitoring system
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.logger.info("Initializing Traffic Monitoring System...")
        
        # Vehicle detector
        self.detector = VehicleDetector(
            model_path=self.config['detection']['model'],
            conf_threshold=self.config['detection']['confidence_threshold']
        )
        
        # Traffic analyzer
        self.analyzer = TrafficAnalyzer(
            num_lanes=self.config['lanes']['count'],
            history_size=30
        )
        
        # Signal controller
        self.controller = SignalController(
            num_lanes=self.config['lanes']['count'],
            config=self.config['signal']
        )
        
        # Video capture
        self.cap = None
        self.out = None
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        
        self.logger.info("System initialized successfully")
    
    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            'detection': {
                'model': 'yolov8n.pt',
                'confidence_threshold': 0.5
            },
            'lanes': {'count': 4},
            'signal': {
                'min_green_time': 10,
                'max_green_time': 60,
                'yellow_time': 3,
                'all_red_time': 2,
                'adaptive_mode': True
            },
            'video': {
                'source': 0,
                'fps': 30
            },
            'output': {
                'show_live_feed': True,
                'save_video': False,
                'log_level': 'INFO'
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config['output'].get('log_level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('data/output/system.log')
            ]
        )
    
    def initialize_video_capture(self, source):
        """Initialize video capture"""
        # Convert source to int if it's a digit (webcam)
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video source: {source}")
        
        # Get video properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.logger.info(f"Video source opened: {source} ({self.frame_width}x{self.frame_height})")
        
        # Initialize video writer if needed
        if self.config['output'].get('save_video', False):
            self.initialize_video_writer()
    
    def initialize_video_writer(self):
        """Initialize video writer for output"""
        output_dir = Path(self.config['output'].get('output_dir', 'data/output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"traffic_output_{int(time.time())}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = self.config['video'].get('fps', 30)
        
        self.out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (self.frame_width, self.frame_height)
        )
        
        self.logger.info(f"Video output: {output_path}")
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect vehicles
        detections = self.detector.detect(frame)
        
        # Analyze traffic
        analysis = self.analyzer.update(detections, frame.shape)
        
        # Update signal controller
        signal_status = self.controller.update(analysis)
        
        # Draw visualizations
        annotated_frame = self.visualize_frame(frame, detections, analysis, signal_status)
        
        return annotated_frame, analysis, signal_status
    
    def visualize_frame(self, frame, detections, analysis, signal_status):
        """Add all visualizations to frame"""
        # Draw vehicle detections
        annotated = self.detector.draw_detections(frame, detections)
        
        # Draw lane information
        annotated = self.analyzer.draw_lane_info(annotated, analysis)
        
        # Draw signal status
        annotated = self.controller.draw_signals(annotated, position=(10, 100))
        
        # Draw statistics panel
        annotated = self.draw_statistics_panel(annotated, analysis, signal_status)
        
        return annotated
    
    def draw_statistics_panel(self, frame, analysis, signal_status):
        """Draw statistics panel on frame"""
        annotated = frame.copy()
        
        # Panel background
        cv2.rectangle(annotated, (10, 450), (300, 650), (0, 0, 0), -1)
        cv2.rectangle(annotated, (10, 450), (300, 650), (255, 255, 255), 2)
        
        # Title
        cv2.putText(annotated, "STATISTICS", (20, 475),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # FPS
        y_pos = 500
        cv2.putText(annotated, f"FPS: {self.fps:.1f}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Total vehicles
        y_pos += 25
        cv2.putText(annotated, f"Total Vehicles: {analysis['total_vehicles']}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Emergency vehicles
        if analysis['emergency_vehicles'] > 0:
            y_pos += 25
            cv2.putText(annotated, f"Emergency: {analysis['emergency_vehicles']}", (20, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Active lane
        y_pos += 25
        cv2.putText(annotated, f"Active Lane: {signal_status['active_lane']}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Cycle count
        y_pos += 25
        cv2.putText(annotated, f"Cycles: {signal_status['cycle_count']}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Runtime
        runtime = time.time() - self.start_time
        y_pos += 25
        cv2.putText(annotated, f"Runtime: {int(runtime)}s", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def run(self, source=None):
        """Run the traffic monitoring system"""
        # Use config source if not specified
        if source is None:
            source = self.config['video']['source']
        
        # Initialize video capture
        self.initialize_video_capture(source)
        
        self.logger.info("Starting traffic monitoring...")
        print("\n" + "="*50)
        print("Smart Traffic Light Monitoring System")
        print("="*50)
        print("Press 'q' to quit")
        print("Press 's' to save screenshot")
        print("="*50 + "\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.logger.warning("End of video stream")
                    break
                
                # Process frame
                start_time = time.time()
                annotated_frame, analysis, signal_status = self.process_frame(frame)
                processing_time = time.time() - start_time
                
                # Calculate FPS
                self.fps = 1.0 / processing_time if processing_time > 0 else 0
                self.frame_count += 1
                
                # Save video if enabled
                if self.out is not None:
                    self.out.write(annotated_frame)
                
                # Display frame
                if self.config['output'].get('show_live_feed', True):
                    cv2.imshow('Traffic Monitoring System', annotated_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.logger.info("User requested quit")
                    break
                elif key == ord('s'):
                    screenshot_path = f"data/output/screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(screenshot_path, annotated_frame)
                    self.logger.info(f"Screenshot saved: {screenshot_path}")
                    print(f"Screenshot saved: {screenshot_path}")
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up...")
        
        # Print final statistics
        stats = self.analyzer.get_statistics()
        print("\n" + "="*50)
        print("FINAL STATISTICS")
        print("="*50)
        print(f"Total Vehicles Detected: {stats['total_vehicles']}")
        print(f"Emergency Vehicles: {stats.get('emergency_vehicles', 0)}")
        print(f"Runtime: {stats['runtime_minutes']:.2f} minutes")
        print(f"Vehicles per Minute: {stats['vehicles_per_minute']:.2f}")
        print("\nLane Statistics:")
        for lane_id, count in stats['lane_totals'].items():
            print(f"  Lane {lane_id}: {count} vehicles")
        print("="*50 + "\n")
        
        # Release resources
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()
        
        self.logger.info("Cleanup complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Smart Traffic Light Monitoring System'
    )
    parser.add_argument(
        '--source',
        type=str,
        default=None,
        help='Video source (0 for webcam, path to video file, or RTSP URL)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--lanes',
        type=int,
        default=None,
        help='Number of lanes to monitor (overrides config)'
    )
    parser.add_argument(
        '--save-output',
        action='store_true',
        help='Save output video'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    Path('data/output').mkdir(parents=True, exist_ok=True)
    
    # Initialize system
    system = TrafficMonitoringSystem(config_path=args.config)
    
    # Override config if specified
    if args.lanes:
        system.config['lanes']['count'] = args.lanes
        system.analyzer.num_lanes = args.lanes
        system.controller.num_lanes = args.lanes
    
    if args.save_output:
        system.config['output']['save_video'] = True
    
    # Run system
    try:
        system.run(source=args.source)
    except Exception as e:
        logging.error(f"System error: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Please check the logs for details.")


if __name__ == "__main__":
    main()
