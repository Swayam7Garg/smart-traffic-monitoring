"""
Traffic Analysis Module
Analyzes traffic patterns and calculates congestion metrics
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import deque
import logging

logger = logging.getLogger(__name__)


class TrafficAnalyzer:
    """Analyzes traffic flow and congestion"""
    
    def __init__(self, history_size: int = 30):
        """
        Initialize traffic analyzer
        
        Args:
            history_size: Number of frames to keep in history
        """
        self.history_size = history_size
        self.vehicle_history = deque(maxlen=history_size)
        self.congestion_threshold = 35  # vehicles (increased for more realistic assessment)
    
    def analyze_frame(self, detections: List[Dict]) -> Dict:
        """
        Analyze traffic in a single frame
        
        Args:
            detections: List of vehicle detections
            
        Returns:
            Analysis results dictionary
        """
        vehicle_count = len(detections)
        self.vehicle_history.append(vehicle_count)
        
        # Calculate congestion level (0-100%)
        congestion_level = min(100, (vehicle_count / self.congestion_threshold) * 100)
        
        # Count vehicles by type
        vehicle_types = {}
        for detection in detections:
            vehicle_type = detection["class_name"]
            vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
        
        # Calculate traffic density
        avg_vehicles = np.mean(self.vehicle_history) if self.vehicle_history else 0
        
        # Determine traffic state (adjusted thresholds for realistic assessment)
        if congestion_level < 40:
            traffic_state = "light"
        elif congestion_level < 70:
            traffic_state = "moderate"
        elif congestion_level < 85:
            traffic_state = "heavy"
        else:
            traffic_state = "congested"
        
        return {
            "vehicle_count": vehicle_count,
            "vehicle_types": vehicle_types,
            "congestion_level": round(congestion_level, 2),
            "avg_vehicle_count": round(avg_vehicles, 2),
            "traffic_state": traffic_state,
            "is_congested": congestion_level >= 85
        }
    
    def calculate_flow_rate(self, time_interval: float = 60.0) -> float:
        """
        Calculate vehicle flow rate (vehicles per minute)
        
        Args:
            time_interval: Time interval in seconds
            
        Returns:
            Flow rate (vehicles/minute)
        """
        if not self.vehicle_history:
            return 0.0
        
        total_vehicles = sum(self.vehicle_history)
        frames = len(self.vehicle_history)
        
        # Assume 30 fps (adjust based on actual frame rate)
        fps = 30
        duration_minutes = (frames / fps) / 60
        
        if duration_minutes > 0:
            return total_vehicles / duration_minutes
        return 0.0
    
    def detect_anomalies(self) -> List[str]:
        """
        Detect traffic anomalies
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        if len(self.vehicle_history) < 10:
            return anomalies
        
        current_count = self.vehicle_history[-1]
        avg_count = np.mean(list(self.vehicle_history)[:-1])
        std_count = np.std(list(self.vehicle_history)[:-1])
        
        # Sudden spike in traffic
        if current_count > avg_count + (2 * std_count):
            anomalies.append("sudden_traffic_increase")
        
        # Sudden drop (possible incident)
        if current_count < avg_count - (2 * std_count) and avg_count > 5:
            anomalies.append("sudden_traffic_decrease")
        
        # Persistent congestion
        recent_counts = list(self.vehicle_history)[-10:]
        if all(count >= self.congestion_threshold for count in recent_counts):
            anomalies.append("persistent_congestion")
        
        return anomalies
    
    def get_peak_hours_prediction(self, historical_data: List[Dict]) -> Dict:
        """
        Predict peak traffic hours based on historical data
        
        Args:
            historical_data: List of historical traffic records
            
        Returns:
            Peak hours prediction
        """
        # Group by hour
        hourly_counts = {}
        for record in historical_data:
            hour = record.get("hour", 0)
            count = record.get("vehicle_count", 0)
            
            if hour not in hourly_counts:
                hourly_counts[hour] = []
            hourly_counts[hour].append(count)
        
        # Calculate average per hour
        hourly_averages = {
            hour: np.mean(counts)
            for hour, counts in hourly_counts.items()
        }
        
        # Find peak hours (top 3)
        sorted_hours = sorted(
            hourly_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        peak_hours = [hour for hour, _ in sorted_hours[:3]]
        
        return {
            "peak_hours": peak_hours,
            "hourly_averages": hourly_averages
        }
    
    def calculate_wait_time_estimate(
        self,
        vehicle_count: int,
        green_time: int = 30
    ) -> float:
        """
        Estimate average wait time at intersection
        
        Args:
            vehicle_count: Number of waiting vehicles
            green_time: Green signal duration in seconds
            
        Returns:
            Estimated wait time in seconds
        """
        # Simple estimation: assume 2 vehicles pass per second during green
        vehicles_per_green = green_time * 2
        
        if vehicle_count <= vehicles_per_green:
            return green_time / 2  # Average wait during one cycle
        
        # Multiple cycles needed
        cycles_needed = np.ceil(vehicle_count / vehicles_per_green)
        cycle_time = green_time * 2  # Assuming equal red/green time
        
        return cycles_needed * cycle_time / 2
