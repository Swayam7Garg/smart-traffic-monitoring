"""
Signal Controller Module
Implements adaptive traffic signal timing based on traffic density
"""

import time
import logging
from typing import Dict, List
from enum import Enum


class SignalState(Enum):
    """Traffic signal states"""
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    ALL_RED = "ALL_RED"


class SignalController:
    """
    Controls traffic signals with adaptive timing
    """
    
    def __init__(self, num_lanes: int = 4, config: Dict = None):
        """
        Initialize signal controller
        
        Args:
            num_lanes: Number of lanes/signals to control
            config: Configuration dictionary with timing parameters
        """
        self.logger = logging.getLogger(__name__)
        self.num_lanes = num_lanes
        
        # Default configuration
        self.config = {
            'min_green_time': 10,
            'max_green_time': 60,
            'yellow_time': 3,
            'all_red_time': 2,
            'adaptive_mode': True,
            'emergency_priority': True,
            'emergency_green_time': 30,
            'density_thresholds': {
                'low': 5,
                'medium': 15,
                'high': 30
            },
            'time_multipliers': {
                'low': 1.0,
                'medium': 1.5,
                'high': 2.0
            }
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        # Initialize signal states
        self.signals = {
            i: {
                'state': SignalState.RED,
                'time_remaining': 0,
                'cycle_start': time.time(),
                'green_time': self.config['min_green_time']
            }
            for i in range(num_lanes)
        }
        
        # Current active lane
        self.active_lane = 0
        self.signals[self.active_lane]['state'] = SignalState.GREEN
        self.signals[self.active_lane]['time_remaining'] = self.config['min_green_time']
        
        # Cycle tracking
        self.cycle_count = 0
        self.cycle_start_time = time.time()
        
        self.logger.info(f"SignalController initialized with {num_lanes} lanes")
    
    def calculate_green_time(self, lane_density: Dict) -> float:
        """
        Calculate optimal green light duration based on traffic density
        
        Args:
            lane_density: Dictionary with density information
            
        Returns:
            Green light duration in seconds
        """
        if not self.config['adaptive_mode']:
            return self.config['min_green_time']
        
        current_density = lane_density.get('current', 0)
        
        # Determine density level
        if current_density >= self.config['density_thresholds']['high']:
            multiplier = self.config['time_multipliers']['high']
        elif current_density >= self.config['density_thresholds']['medium']:
            multiplier = self.config['time_multipliers']['medium']
        else:
            multiplier = self.config['time_multipliers']['low']
        
        # Calculate time
        green_time = self.config['min_green_time'] * multiplier
        
        # Apply bounds
        green_time = max(self.config['min_green_time'], 
                        min(green_time, self.config['max_green_time']))
        
        return green_time
    
    def handle_emergency(self, lane_id: int) -> None:
        """
        Handle emergency vehicle priority
        
        Args:
            lane_id: Lane with emergency vehicle
        """
        if not self.config['emergency_priority']:
            return
        
        self.logger.warning(f"Emergency vehicle detected in lane {lane_id}")
        
        # Immediately switch to yellow for current green
        if self.active_lane != lane_id:
            current_signal = self.signals[self.active_lane]
            if current_signal['state'] == SignalState.GREEN:
                current_signal['state'] = SignalState.YELLOW
                current_signal['time_remaining'] = self.config['yellow_time']
            
            # Set emergency lane to activate next
            self.next_lane = lane_id
            self.emergency_mode = True
    
    def update(self, analysis: Dict) -> Dict:
        """
        Update signal states based on traffic analysis
        
        Args:
            analysis: Traffic analysis results
            
        Returns:
            Current signal states
        """
        current_time = time.time()
        
        # Check for emergency vehicles
        if analysis.get('has_emergency', False):
            for lane_id, lane_data in analysis['lanes'].items():
                if lane_data.get('emergency', 0) > 0:
                    self.handle_emergency(lane_id)
                    break
        
        # Update active signal
        active_signal = self.signals[self.active_lane]
        time_elapsed = current_time - active_signal['cycle_start']
        
        # State machine
        if active_signal['state'] == SignalState.GREEN:
            if time_elapsed >= active_signal['green_time']:
                # Switch to yellow
                active_signal['state'] = SignalState.YELLOW
                active_signal['cycle_start'] = current_time
                active_signal['time_remaining'] = self.config['yellow_time']
                self.logger.info(f"Lane {self.active_lane}: GREEN -> YELLOW")
        
        elif active_signal['state'] == SignalState.YELLOW:
            if time_elapsed >= self.config['yellow_time']:
                # Switch to red
                active_signal['state'] = SignalState.RED
                active_signal['cycle_start'] = current_time
                
                # All signals to red briefly
                for signal in self.signals.values():
                    signal['state'] = SignalState.RED
                
                self.logger.info(f"Lane {self.active_lane}: YELLOW -> ALL RED")
                
                # Wait for all-red time before switching
                time.sleep(self.config['all_red_time'])
                
                # Determine next lane
                self.switch_to_next_lane(analysis)
        
        # Update time remaining for all signals
        for lane_id, signal in self.signals.items():
            if lane_id == self.active_lane:
                signal['time_remaining'] = max(0, signal['green_time'] - time_elapsed)
        
        # Prepare response
        response = {
            'active_lane': self.active_lane,
            'signals': {
                lane_id: {
                    'state': signal['state'].value,
                    'time_remaining': signal.get('time_remaining', 0)
                }
                for lane_id, signal in self.signals.items()
            },
            'cycle_count': self.cycle_count
        }
        
        return response
    
    def switch_to_next_lane(self, analysis: Dict) -> None:
        """
        Switch to next lane with highest priority
        
        Args:
            analysis: Traffic analysis results
        """
        # Calculate priority for each lane
        priorities = {}
        
        for lane_id in range(self.num_lanes):
            if lane_id == self.active_lane:
                priorities[lane_id] = -1  # Don't switch to same lane
                continue
            
            lane_data = analysis['lanes'].get(lane_id, {})
            
            # Check for emergency
            if lane_data.get('emergency', 0) > 0:
                priorities[lane_id] = 1000  # Highest priority
                continue
            
            # Calculate priority based on density and wait time
            density = lane_data.get('density', {})
            current_density = density.get('current', 0)
            trend = density.get('trend', 'stable')
            
            # Base priority on vehicle count
            priority = current_density
            
            # Bonus for increasing trend
            if trend == 'increasing':
                priority *= 1.2
            
            priorities[lane_id] = priority
        
        # Select lane with highest priority
        next_lane = max(priorities, key=priorities.get)
        
        # Update next lane signal
        lane_data = analysis['lanes'].get(next_lane, {})
        density = lane_data.get('density', {})
        
        # Calculate green time for next lane
        green_time = self.calculate_green_time(density)
        
        # Override for emergency
        if lane_data.get('emergency', 0) > 0:
            green_time = self.config['emergency_green_time']
        
        # Activate next lane
        self.active_lane = next_lane
        self.signals[next_lane]['state'] = SignalState.GREEN
        self.signals[next_lane]['cycle_start'] = time.time()
        self.signals[next_lane]['green_time'] = green_time
        self.signals[next_lane]['time_remaining'] = green_time
        
        self.cycle_count += 1
        
        self.logger.info(f"Switched to Lane {next_lane} (GREEN for {green_time:.1f}s, "
                        f"density: {density.get('current', 0)})")
    
    def get_signal_state(self, lane_id: int) -> str:
        """
        Get current state of a signal
        
        Args:
            lane_id: Lane identifier
            
        Returns:
            Signal state as string
        """
        return self.signals[lane_id]['state'].value
    
    def draw_signals(self, frame, position=(10, 100)):
        """
        Draw signal status on frame
        
        Args:
            frame: Input frame
            position: Starting position for drawing
            
        Returns:
            Frame with signal status
        """
        import cv2
        import numpy as np
        
        annotated = frame.copy()
        x, y = position
        
        # Draw signal panel background
        panel_height = 30 + self.num_lanes * 40
        cv2.rectangle(annotated, (x - 5, y - 25), (x + 200, y + panel_height), 
                     (0, 0, 0), -1)
        cv2.rectangle(annotated, (x - 5, y - 25), (x + 200, y + panel_height), 
                     (255, 255, 255), 2)
        
        # Title
        cv2.putText(annotated, "SIGNALS", (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw each signal
        for lane_id in range(self.num_lanes):
            signal = self.signals[lane_id]
            state = signal['state']
            time_remaining = signal.get('time_remaining', 0)
            
            y_pos = y + 10 + lane_id * 40
            
            # Lane label
            cv2.putText(annotated, f"Lane {lane_id}:", (x, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Signal light
            color_map = {
                SignalState.RED: (0, 0, 255),
                SignalState.YELLOW: (0, 255, 255),
                SignalState.GREEN: (0, 255, 0),
                SignalState.ALL_RED: (0, 0, 128)
            }
            
            color = color_map.get(state, (128, 128, 128))
            cv2.circle(annotated, (x + 100, y_pos - 5), 12, color, -1)
            cv2.circle(annotated, (x + 100, y_pos - 5), 12, (255, 255, 255), 2)
            
            # Time remaining
            if state == SignalState.GREEN:
                time_text = f"{int(time_remaining)}s"
                cv2.putText(annotated, time_text, (x + 130, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated


if __name__ == "__main__":
    """
    Test signal controller
    """
    logging.basicConfig(level=logging.INFO)
    
    # Create controller
    controller = SignalController(num_lanes=4)
    
    # Simulate traffic analysis
    analysis = {
        'has_emergency': False,
        'lanes': {
            0: {'vehicles': 5, 'emergency': 0, 'density': {'current': 5, 'trend': 'stable'}},
            1: {'vehicles': 15, 'emergency': 0, 'density': {'current': 15, 'trend': 'increasing'}},
            2: {'vehicles': 8, 'emergency': 0, 'density': {'current': 8, 'trend': 'stable'}},
            3: {'vehicles': 3, 'emergency': 0, 'density': {'current': 3, 'trend': 'decreasing'}}
        }
    }
    
    # Update controller
    response = controller.update(analysis)
    
    print("\nSignal States:")
    for lane_id, signal_info in response['signals'].items():
        print(f"Lane {lane_id}: {signal_info['state']} "
              f"({signal_info['time_remaining']:.1f}s remaining)")
    
    print(f"\nActive Lane: {response['active_lane']}")
    print(f"Cycle Count: {response['cycle_count']}")
