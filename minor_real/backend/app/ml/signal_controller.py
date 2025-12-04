"""
Signal Controller Module
Adaptive traffic signal timing based on real-time traffic data
"""

from typing import Dict, List
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class SignalController:
    """Adaptive traffic signal controller"""
    
    def __init__(
        self,
        min_green_time: int = 15,
        max_green_time: int = 120,
        default_green_time: int = 30
    ):
        """
        Initialize signal controller
        
        Args:
            min_green_time: Minimum green signal duration (seconds)
            max_green_time: Maximum green signal duration (seconds)
            default_green_time: Default green signal duration (seconds)
        """
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        self.default_green_time = default_green_time
        
        # Signal states
        self.current_phases = {}
        self.last_update = datetime.utcnow()
    
    def calculate_adaptive_timing(
        self,
        traffic_data: Dict[str, int]
    ) -> Dict[str, int]:
        """
        Calculate adaptive signal timing based on traffic volume
        
        Args:
            traffic_data: Dictionary with direction as key and vehicle count as value
                         e.g., {"north_south": 25, "east_west": 10}
        
        Returns:
            Dictionary with green time for each direction
        """
        if not traffic_data:
            return {}
        
        total_vehicles = sum(traffic_data.values())
        if total_vehicles == 0:
            # No traffic, use default timings
            return {
                direction: self.default_green_time
                for direction in traffic_data.keys()
            }
        
        # Proportional timing based on traffic volume
        timings = {}
        for direction, count in traffic_data.items():
            # Calculate proportional time
            proportion = count / total_vehicles
            green_time = int(proportion * (self.max_green_time - self.min_green_time) + self.min_green_time)
            
            # Clamp to min/max bounds
            green_time = max(self.min_green_time, min(self.max_green_time, green_time))
            timings[direction] = green_time
        
        logger.info(f"Adaptive timing calculated: {timings}")
        return timings
    
    def optimize_cycle_length(
        self,
        traffic_volumes: Dict[str, int],
        peak_hour: bool = False
    ) -> int:
        """
        Optimize total cycle length based on traffic conditions
        
        Args:
            traffic_volumes: Traffic volumes for each direction
            peak_hour: Whether it's peak traffic hour
            
        Returns:
            Optimized cycle length in seconds
        """
        total_vehicles = sum(traffic_volumes.values())
        
        # Base cycle length
        if peak_hour:
            base_cycle = 120  # Longer cycles during peak hours
        else:
            base_cycle = 90
        
        # Adjust based on total traffic
        if total_vehicles < 10:
            cycle_length = 60  # Short cycle for light traffic
        elif total_vehicles < 30:
            cycle_length = base_cycle
        elif total_vehicles < 50:
            cycle_length = base_cycle + 30
        else:
            cycle_length = base_cycle + 60
        
        # Ensure it doesn't exceed maximum
        return min(cycle_length, 240)
    
    def priority_override(
        self,
        direction: str,
        priority_level: str = "emergency"
    ) -> Dict:
        """
        Override signal for priority vehicles (emergency, public transport)
        
        Args:
            direction: Direction requiring priority
            priority_level: emergency/public_transport
            
        Returns:
            Override configuration
        """
        if priority_level == "emergency":
            # Immediate green for emergency vehicles
            override_time = self.max_green_time
            clear_time = 10  # Extra seconds to clear intersection
        elif priority_level == "public_transport":
            # Extended green for buses
            override_time = self.default_green_time + 15
            clear_time = 5
        else:
            override_time = self.default_green_time
            clear_time = 0
        
        return {
            "direction": direction,
            "green_time": override_time,
            "clear_time": clear_time,
            "priority_level": priority_level,
            "timestamp": datetime.utcnow()
        }
    
    def generate_signal_plan(
        self,
        intersection_id: str,
        traffic_data: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Generate complete signal plan for an intersection
        
        Args:
            intersection_id: Intersection identifier
            traffic_data: Traffic data for all approaches
                         e.g., {"north": {...}, "south": {...}, ...}
        
        Returns:
            List of signal phases with timing
        """
        # Extract vehicle counts per direction
        direction_counts = {}
        for direction, data in traffic_data.items():
            direction_counts[direction] = data.get("vehicle_count", 0)
        
        # Calculate adaptive timings
        timings = self.calculate_adaptive_timing(direction_counts)
        
        # Create signal phases
        phases = []
        yellow_time = 5  # Standard yellow time
        all_red_time = 2  # Safety clearance
        
        # Group opposing directions (e.g., north-south, east-west)
        direction_groups = self._group_directions(list(direction_counts.keys()))
        
        for group in direction_groups:
            # Get max green time for this group
            max_green = max(timings.get(d, self.default_green_time) for d in group)
            
            phases.append({
                "directions": group,
                "green_time": max_green,
                "yellow_time": yellow_time,
                "all_red_time": all_red_time,
                "total_time": max_green + yellow_time + all_red_time
            })
        
        # Calculate total cycle time
        total_cycle = sum(phase["total_time"] for phase in phases)
        
        return {
            "intersection_id": intersection_id,
            "phases": phases,
            "cycle_length": total_cycle,
            "is_adaptive": True,
            "generated_at": datetime.utcnow()
        }
    
    def _group_directions(self, directions: List[str]) -> List[List[str]]:
        """Group compatible traffic directions"""
        # Simple grouping logic - can be enhanced based on intersection geometry
        groups = []
        
        # Group opposing directions together
        if "north" in directions and "south" in directions:
            groups.append(["north", "south"])
        elif "north" in directions:
            groups.append(["north"])
        elif "south" in directions:
            groups.append(["south"])
        
        if "east" in directions and "west" in directions:
            groups.append(["east", "west"])
        elif "east" in directions:
            groups.append(["east"])
        elif "west" in directions:
            groups.append(["west"])
        
        # If no standard directions, create single group
        if not groups:
            groups = [[d] for d in directions]
        
        return groups
    
    def evaluate_efficiency(
        self,
        vehicle_counts: Dict[str, int],
        signal_timings: Dict[str, int]
    ) -> float:
        """
        Evaluate signal timing efficiency
        
        Args:
            vehicle_counts: Current vehicle counts per direction
            signal_timings: Current signal timings
            
        Returns:
            Efficiency score (0-100)
        """
        if not vehicle_counts or not signal_timings:
            return 0.0
        
        total_vehicles = sum(vehicle_counts.values())
        total_green_time = sum(signal_timings.values())
        
        if total_green_time == 0:
            return 0.0
        
        # Calculate how well timing matches demand
        efficiency_scores = []
        for direction, count in vehicle_counts.items():
            if direction in signal_timings:
                # Ideal: green time proportion matches traffic proportion
                traffic_proportion = count / total_vehicles if total_vehicles > 0 else 0
                time_proportion = signal_timings[direction] / total_green_time
                
                # Difference from ideal (0 is perfect)
                diff = abs(traffic_proportion - time_proportion)
                efficiency = 1 - diff
                efficiency_scores.append(efficiency)
        
        # Average efficiency as percentage
        avg_efficiency = np.mean(efficiency_scores) * 100 if efficiency_scores else 0
        return round(avg_efficiency, 2)
