"""
Advanced Traffic Monitoring System
Integrates ALL unique features: Web Dashboard, Alerts, and Reports
"""

import cv2
import argparse
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.vehicle_detector import VehicleDetector
from src.traffic_analyzer import TrafficAnalyzer
from src.signal_controller import SignalController
from src.alert_system import AlertSystem
from src.report_generator import TrafficReportGenerator
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AdvancedTrafficSystem:
    """
    Advanced Traffic Monitoring System with:
    - Real-time vehicle detection
    - Adaptive signal control
    - Email alerts
    - Report generation
    """
    
    def __init__(self, source=0, save_output=False):
        """Initialize the advanced system"""
        logger.info("Initializing Advanced Traffic Monitoring System...")
        
        # Load configuration
        self.config = ConfigManager().config
        
        # Initialize core components
        self.detector = VehicleDetector(model_path='yolov8n.pt')
        self.analyzer = TrafficAnalyzer(num_lanes=4)
        self.controller = SignalController(num_lanes=4)
        
        # Initialize NEW features
        self.alert_system = AlertSystem()
        self.report_gen = TrafficReportGenerator()
        
        # Video settings
        self.source = source
        self.save_output = save_output
        self.output_path = None
        
        if self.save_output:
            output_dir = Path('data/output')
            output_dir.mkdir(parents=True, exist_ok=True)
            self.output_path = output_dir / f'traffic_output_{int(cv2.getTickCount())}.mp4'
        
        logger.info("✅ All components initialized!")
        
        if self.alert_system.enabled:
            logger.info("✅ Email alerts enabled")
        else:
            logger.info("⚠️  Email alerts disabled (configure in config/alert_config.yaml)")
    
    def process_frame(self, frame):
        """Process a single frame with all features"""
        # Core detection and analysis
        detections = self.detector.detect(frame)
        analysis = self.analyzer.update(detections, frame.shape)
        signal_status = self.controller.update(analysis)
        
        # NEW FEATURE 1: Check for alerts
        self.alert_system.check_congestion(analysis)
        self.alert_system.check_emergency(analysis)
        
        # NEW FEATURE 2: Log data for reports
        self.report_gen.log_frame_data(analysis, signal_status)
        
        return detections, analysis, signal_status
    
    def visualize_frame(self, frame, detections, analysis, signal_status):
        """Visualize detection results on frame"""
        annotated = self.detector.draw_detections(frame, detections)
        annotated = self.analyzer.draw_lane_info(annotated, analysis)
        annotated = self.controller.draw_signals(annotated)
        
        # Add feature indicators
        y_offset = 30
        if self.alert_system.enabled:
            cv2.putText(annotated, "Alerts: ON", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 30
        
        cv2.putText(annotated, "Reports: Logging", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return annotated
    
    def run(self):
        """Run the advanced monitoring system"""
        logger.info("\n" + "="*60)
        logger.info("  🚀 ADVANCED TRAFFIC MONITORING SYSTEM")
        logger.info("="*60)
        logger.info(f"Source: {self.source}")
        logger.info(f"Features:")
        logger.info(f"  ✅ Vehicle Detection (YOLOv8)")
        logger.info(f"  ✅ Adaptive Signal Control")
        logger.info(f"  {'✅' if self.alert_system.enabled else '⚠️'} Email Alerts")
        logger.info(f"  ✅ Report Generation")
        logger.info(f"  {'✅' if self.save_output else '❌'} Video Output")
        logger.info("="*60 + "\n")
        
        # Open video source
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            logger.error(f"Failed to open video source: {self.source}")
            return
        
        # Setup video writer
        writer = None
        if self.save_output:
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(self.output_path), fourcc, fps, (width, height))
            logger.info(f"📹 Saving output to: {self.output_path}")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video or camera disconnected")
                    break
                
                frame_count += 1
                
                # Process frame with all features
                detections, analysis, signal_status = self.process_frame(frame)
                
                # Visualize
                annotated = self.visualize_frame(frame, detections, analysis, signal_status)
                
                # Save frame
                if writer:
                    writer.write(annotated)
                
                # Display
                cv2.imshow('Advanced Traffic Monitoring System', annotated)
                
                # Status update every 30 frames
                if frame_count % 30 == 0:
                    logger.info(f"Frame {frame_count}: "
                              f"Vehicles={analysis['total_vehicles']}, "
                              f"Emergency={analysis['emergency_vehicles']}, "
                              f"Active Lane={signal_status['active_lane']+1}")
                
                # Exit on 'q' or ESC
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    logger.info("User requested exit")
                    break
        
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            self.alert_system.send_system_error(str(e))
        
        finally:
            # Cleanup
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            
            # Generate final statistics
            self.print_statistics()
            
            # NEW FEATURE 3: Generate reports
            self.generate_final_reports()
    
    def print_statistics(self):
        """Print session statistics"""
        stats = self.analyzer.get_statistics()
        
        logger.info("\n" + "="*60)
        logger.info("  📊 SESSION STATISTICS")
        logger.info("="*60)
        logger.info(f"Total Frames Processed: {stats['frames_processed']}")
        logger.info(f"Total Vehicles Detected: {stats['total_vehicles']}")
        logger.info(f"Average Vehicles/Frame: {stats['avg_vehicles_per_frame']:.2f}")
        
        logger.info("\n🚗 Vehicle Types:")
        for vehicle_type, count in stats['vehicle_types'].items():
            logger.info(f"  {vehicle_type}: {count}")
        
        logger.info("\n🚦 Lane Statistics:")
        for i, lane in enumerate(stats['lanes']):
            logger.info(f"  Lane {i+1}: {lane['total_vehicles']} vehicles "
                       f"(avg: {lane['avg_vehicles']:.1f})")
        
        emergency_count = stats.get('emergency_vehicles', 0)
        logger.info(f"\n🚨 Emergency Vehicles: {emergency_count}")
        
        logger.info("="*60 + "\n")
    
    def generate_final_reports(self):
        """Generate all reports at end of session"""
        logger.info("📊 Generating comprehensive reports...")
        
        try:
            reports = self.report_gen.generate_all_reports()
            
            if reports:
                logger.info("\n✅ Reports generated successfully!")
                logger.info(f"📁 Location: {self.report_gen.output_dir}")
                
                for report_type, filepath in reports.items():
                    logger.info(f"  {report_type.upper()}: {Path(filepath).name}")
            else:
                logger.warning("⚠️  No reports generated (insufficient data)")
        
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Advanced Traffic Monitoring System with Alerts and Reports'
    )
    parser.add_argument(
        '--source',
        type=str,
        default='0',
        help='Video source (0 for webcam, path to video file, or RTSP URL)'
    )
    parser.add_argument(
        '--save-output',
        action='store_true',
        help='Save output video'
    )
    
    args = parser.parse_args()
    
    # Convert source
    source = args.source
    if source.isdigit():
        source = int(source)
    
    # Create and run system
    system = AdvancedTrafficSystem(
        source=source,
        save_output=args.save_output
    )
    
    system.run()


if __name__ == '__main__':
    main()
