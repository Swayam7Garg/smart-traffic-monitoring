"""
Traffic Analyzer Module
Analyzes traffic density and patterns for signal optimization
"""

import numpy as np
from typing import List, Dict, Tuple
import logging
from collections import deque
import time


class TrafficAnalyzer:
    """
    Analyzes traffic patterns and calculates optimal signal timing
    """
    
    def __init__(self, num_lanes: int = 4, history_size: int = 30):
        """
        Initialize traffic analyzer
        
        Args:
            num_lanes: Number of lanes to monitor
            history_size: Number of frames to keep in history
        """
        self.logger = logging.getLogger(__name__)
        self.num_lanes = num_lanes
        self.history_size = history_size
        
        # Initialize history for each lane
        self.lane_history = {
            i: deque(maxlen=history_size) for i in range(num_lanes)
        }
        
        # Statistics
        self.stats = {
            'total_vehicles': 0,
            'emergency_count': 0,
            'lane_totals': {i: 0 for i in range(num_lanes)},
            'start_time': time.time()
        }
        
        self.logger.info(f"TrafficAnalyzer initialized with {num_lanes} lanes")
    
    def assign_to_lane(self, detections: List[Dict], frame_shape: Tuple[int, int]) -> Dict[int, List[Dict]]:
        """
        Assign detected vehicles to lanes based on position
        
        Args:
            detections: List of vehicle detections
            frame_shape: (height, width) of frame
            
        Returns:
            Dictionary mapping lane_id to list of detections
        """
        height, width = frame_shape[:2]
        lane_detections = {i: [] for i in range(self.num_lanes)}
        
        # Simple quadrant-based lane assignment
        # Customize based on actual camera view
        for detection in detections:
            x, y = detection['center']
            
            # Determine lane based on position
            if self.num_lanes == 4:
                # 4-way intersection
                if x < width / 2 and y < height / 2:
                    lane = 0  # Top-left
                elif x >= width / 2 and y < height / 2:
                    lane = 1  # Top-right
                elif x < width / 2 and y >= height / 2:
                    lane = 2  # Bottom-left
                else:
                    lane = 3  # Bottom-right
            elif self.num_lanes == 2:
                # 2-way (left/right)
                lane = 0 if x < width / 2 else 1
            else:
                # Default: divide frame into equal vertical strips
                lane = min(int(x / (width / self.num_lanes)), self.num_lanes - 1)
            
            lane_detections[lane].append(detection)
        
        return lane_detections
    
    def calculate_density(self, lane_id: int) -> Dict[str, float]:
        """
        Calculate traffic density for a lane
        
        Args:
            lane_id: Lane identifier
            
        Returns:
            Dictionary with density metrics
        """
        if not self.lane_history[lane_id]:
            return {
                'current': 0,
                'average': 0,
                'max': 0,
                'trend': 'stable'
            }
        
        history = list(self.lane_history[lane_id])
        current = history[-1] if history else 0
        average = np.mean(history)
        max_count = max(history)
        
        # Calculate trend
        if len(history) >= 5:
            recent = np.mean(history[-5:])
            older = np.mean(history[:-5])
            if recent > older * 1.2:
                trend = 'increasing'
            elif recent < older * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'current': float(current),
            'average': float(average),
            'max': float(max_count),
            'trend': trend
        }
    
    def update(self, detections: List[Dict], frame_shape: Tuple[int, int]) -> Dict:
        """
        Update traffic analysis with new detections
        
        Args:
            detections: List of vehicle detections
            frame_shape: (height, width) of frame
            
        Returns:
            Analysis results
        """
        # Assign vehicles to lanes
        lane_detections = self.assign_to_lane(detections, frame_shape)
        
        # Update history and statistics
        emergency_in_frame = 0
        lane_info = {}
        
        for lane_id in range(self.num_lanes):
            vehicles_in_lane = len(lane_detections[lane_id])
            self.lane_history[lane_id].append(vehicles_in_lane)
            self.stats['lane_totals'][lane_id] += vehicles_in_lane
            
            # Check for emergency vehicles
            emergency_count = sum(1 for d in lane_detections[lane_id] if d['is_emergency'])
            emergency_in_frame += emergency_count
            
            # Calculate density
            density = self.calculate_density(lane_id)
            
            lane_info[lane_id] = {
                'vehicles': vehicles_in_lane,
                'emergency': emergency_count,
                'density': density,
                'detections': lane_detections[lane_id]
            }
        
        # Update global stats
        self.stats['total_vehicles'] += len(detections)
        self.stats['emergency_count'] += emergency_in_frame
        
        # Prepare analysis result
        analysis = {
            'timestamp': time.time(),
            'total_vehicles': len(detections),
            'emergency_vehicles': emergency_in_frame,
            'lanes': lane_info,
            'has_emergency': emergency_in_frame > 0
        }
        
        return analysis
    
    def get_congestion_level(self, lane_id: int, thresholds: Dict[str, int] = None) -> str:
        """
        Determine congestion level for a lane
        
        Args:
            lane_id: Lane identifier
            thresholds: Dictionary with 'low', 'medium', 'high' thresholds
            
        Returns:
            Congestion level: 'none', 'low', 'medium', 'high'
        """
        if thresholds is None:
            thresholds = {'low': 5, 'medium': 15, 'high': 30}
        
        density = self.calculate_density(lane_id)
        current = density['current']
        
        if current == 0:
            return 'none'
        elif current < thresholds['low']:
            return 'low'
        elif current < thresholds['medium']:
            return 'medium'
        else:
            return 'high'
    
    def get_statistics(self) -> Dict:
        """
        Get cumulative statistics
        
        Returns:
            Dictionary with statistics
        """
        elapsed_time = time.time() - self.stats['start_time']
        
        stats = {
            'total_vehicles': self.stats['total_vehicles'],
            'emergency_vehicles': self.stats['emergency_count'],
            'runtime_seconds': elapsed_time,
            'runtime_minutes': elapsed_time / 60,
            'vehicles_per_minute': self.stats['total_vehicles'] / (elapsed_time / 60) if elapsed_time > 0 else 0,
            'lane_totals': self.stats['lane_totals']
        }
        
        return stats
    
    def draw_lane_info(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        """
        Draw lane information on frame
        
        Args:
            frame: Input frame
            analysis: Analysis results from update()
            
        Returns:
            Frame with lane information
        """
        import cv2
        
        annotated = frame.copy()
        height, width = frame.shape[:2]
        
        # Draw lane dividers (for 4 lanes)
        if self.num_lanes == 4:
            # Vertical line
            cv2.line(annotated, (width // 2, 0), (width // 2, height), (255, 255, 255), 2)
            # Horizontal line
            cv2.line(annotated, (0, height // 2), (width, height // 2), (255, 255, 255), 2)
            
            # Lane labels and counts
            positions = [
                (width // 4, height // 4),      # Lane 0
                (3 * width // 4, height // 4),  # Lane 1
                (width // 4, 3 * height // 4),  # Lane 2
                (3 * width // 4, 3 * height // 4)  # Lane 3
            ]
        elif self.num_lanes == 2:
            cv2.line(annotated, (width // 2, 0), (width // 2, height), (255, 255, 255), 2)
            positions = [
                (width // 4, height // 2),
                (3 * width // 4, height // 2)
            ]
        else:
            positions = [(width // (2 * self.num_lanes) + i * (width // self.num_lanes), height // 2) 
                        for i in range(self.num_lanes)]
        
        # Draw lane info
        for lane_id, pos in enumerate(positions):
            if lane_id in analysis['lanes']:
                lane_data = analysis['lanes'][lane_id]
                vehicles = lane_data['vehicles']
                emergency = lane_data['emergency']
                congestion = self.get_congestion_level(lane_id)
                
                # Color based on congestion
                color_map = {
                    'none': (0, 255, 0),      # Green
                    'low': (0, 255, 255),     # Yellow
                    'medium': (0, 165, 255),  # Orange
                    'high': (0, 0, 255)       # Red
                }
                color = color_map.get(congestion, (255, 255, 255))
                
                # Draw background
                cv2.circle(annotated, pos, 60, color, -1)
                cv2.circle(annotated, pos, 60, (255, 255, 255), 2)
                
                # Draw text
                text = f"L{lane_id}"
                cv2.putText(annotated, text, (pos[0] - 20, pos[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                
                text = f"{vehicles}"
                cv2.putText(annotated, text, (pos[0] - 15, pos[1] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
                
                if emergency > 0:
                    cv2.putText(annotated, "EMG!", (pos[0] - 25, pos[1] + 45),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated


if __name__ == "__main__":
    """
    Test traffic analyzer
    """
    logging.basicConfig(level=logging.INFO)
    
    # Create analyzer
    analyzer = TrafficAnalyzer(num_lanes=4)
    
    # Simulate detections
    test_detections = [
        {'center': (100, 100), 'is_emergency': False},
        {'center': (600, 100), 'is_emergency': False},
        {'center': (100, 500), 'is_emergency': True},
        {'center': (600, 500), 'is_emergency': False},
    ]
    
    frame_shape = (720, 1280)
    
    # Update analyzer
    analysis = analyzer.update(test_detections, frame_shape)
    
    print("\nAnalysis Results:")
    print(f"Total vehicles: {analysis['total_vehicles']}")
    print(f"Emergency vehicles: {analysis['emergency_vehicles']}")
    
    for lane_id, lane_data in analysis['lanes'].items():
        print(f"\nLane {lane_id}:")
        print(f"  Vehicles: {lane_data['vehicles']}")
        print(f"  Emergency: {lane_data['emergency']}")
        print(f"  Density: {lane_data['density']}")
        print(f"  Congestion: {analyzer.get_congestion_level(lane_id)}")
    
    print("\nStatistics:")
    print(analyzer.get_statistics())
