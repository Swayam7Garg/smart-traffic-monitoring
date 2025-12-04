"""
Emergency Vehicle Priority System
Handles automatic signal override when emergency vehicles are detected
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from ..ml.detector import VehicleDetector
from ..ml.signal_controller import SignalController
from ..database import get_signals_collection, get_traffic_collection

logger = logging.getLogger(__name__)


class EmergencyPrioritySystem:
    """Manages emergency vehicle detection and signal priority"""
    
    def __init__(
        self,
        signal_controller: SignalController,
        priority_duration: int = 60,  # seconds
        clear_time: int = 10  # seconds
    ):
        """
        Initialize emergency priority system
        
        Args:
            signal_controller: SignalController instance
            priority_duration: How long to maintain priority (seconds)
            clear_time: Time to clear intersection (seconds)
        """
        self.signal_controller = signal_controller
        self.priority_duration = priority_duration
        self.clear_time = clear_time
        
        # Track active emergency overrides
        self.active_overrides = {}
    
    async def handle_emergency_detection(
        self,
        location_id: str,
        direction: str,
        emergency_vehicles: List[Dict]
    ) -> Dict:
        """
        Handle emergency vehicle detection and trigger signal override
        
        Args:
            location_id: Intersection/location identifier
            direction: Direction of emergency vehicle (north, south, east, west)
            emergency_vehicles: List of emergency vehicle detections
            
        Returns:
            Override response with signal timing
        """
        if not emergency_vehicles:
            return {"status": "no_emergency", "override": False}
        
        logger.warning(f"🚨 EMERGENCY VEHICLE DETECTED at {location_id} from {direction}")
        logger.info(f"Emergency vehicles: {len(emergency_vehicles)}")
        
        # Determine emergency type (ambulance, police, fire)
        emergency_type = self._classify_emergency_type(emergency_vehicles)
        
        # Generate priority signal override
        override = self.signal_controller.priority_override(
            direction=direction,
            priority_level="emergency"
        )
        
        # Store override in active tracking
        override_id = f"{location_id}_{direction}_{datetime.utcnow().timestamp()}"
        self.active_overrides[override_id] = {
            "location_id": location_id,
            "direction": direction,
            "emergency_type": emergency_type,
            "vehicle_count": len(emergency_vehicles),
            "started_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.priority_duration),
            "override_config": override
        }
        
        # Update signal timing in database
        await self._apply_signal_override(location_id, direction, override)
        
        # Log emergency event
        await self._log_emergency_event(location_id, direction, emergency_vehicles)
        
        return {
            "status": "emergency_override_active",
            "override": True,
            "override_id": override_id,
            "location_id": location_id,
            "direction": direction,
            "emergency_type": emergency_type,
            "green_time": override["green_time"],
            "clear_time": override["clear_time"],
            "expires_at": self.active_overrides[override_id]["expires_at"].isoformat(),
            "message": f"🚨 {emergency_type.upper()} PRIORITY ACTIVATED - All other directions RED"
        }
    
    def _classify_emergency_type(self, emergency_vehicles: List[Dict]) -> str:
        """
        Classify emergency vehicle type based on detection
        
        Args:
            emergency_vehicles: List of emergency detections
            
        Returns:
            Emergency type: 'ambulance', 'police', 'fire', or 'emergency'
        """
        # This is a simplified classification
        # In production, use more sophisticated methods (OCR on markings, etc.)
        
        if not emergency_vehicles:
            return "emergency"
        
        # Check vehicle types
        vehicle_types = [v.get("class_name", "") for v in emergency_vehicles]
        
        # Heuristics (can be improved with custom model)
        if "bus" in vehicle_types or "truck" in vehicle_types:
            return "fire"  # Fire trucks are larger
        elif "car" in vehicle_types:
            return "ambulance"  # Most ambulances are vans/cars
        
        return "emergency"
    
    async def _apply_signal_override(
        self,
        location_id: str,
        priority_direction: str,
        override_config: Dict
    ):
        """
        Apply signal override to database
        
        Args:
            location_id: Location identifier
            priority_direction: Direction to prioritize
            override_config: Signal override configuration
        """
        try:
            collection = await get_signals_collection()
            
            # Update signal with emergency override
            await collection.update_one(
                {"location_id": location_id},
                {
                    "$set": {
                        "emergency_override": True,
                        "priority_direction": priority_direction,
                        "override_config": override_config,
                        "override_started": datetime.utcnow(),
                        "last_updated": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info(f"✓ Signal override applied at {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to apply signal override: {e}")
    
    async def _log_emergency_event(
        self,
        location_id: str,
        direction: str,
        emergency_vehicles: List[Dict]
    ):
        """
        Log emergency vehicle event to database
        
        Args:
            location_id: Location identifier
            direction: Direction
            emergency_vehicles: Emergency vehicle detections
        """
        try:
            collection = await get_traffic_collection()
            
            event = {
                "event_type": "emergency_vehicle",
                "location_id": location_id,
                "direction": direction,
                "timestamp": datetime.utcnow(),
                "vehicle_count": len(emergency_vehicles),
                "vehicles": emergency_vehicles,
                "priority_activated": True
            }
            
            await collection.insert_one(event)
            logger.info(f"✓ Emergency event logged")
            
        except Exception as e:
            logger.error(f"Failed to log emergency event: {e}")
    
    async def check_expired_overrides(self):
        """
        Check and clear expired emergency overrides
        Should be called periodically
        """
        current_time = datetime.utcnow()
        expired = []
        
        for override_id, override_data in self.active_overrides.items():
            if current_time >= override_data["expires_at"]:
                expired.append(override_id)
                
                # Clear override from database
                await self._clear_signal_override(override_data["location_id"])
                
                logger.info(f"✓ Emergency override expired: {override_id}")
        
        # Remove expired overrides
        for override_id in expired:
            del self.active_overrides[override_id]
        
        return len(expired)
    
    async def _clear_signal_override(self, location_id: str):
        """Clear emergency override from signal"""
        try:
            collection = await get_signals_collection()
            
            await collection.update_one(
                {"location_id": location_id},
                {
                    "$set": {
                        "emergency_override": False,
                        "priority_direction": None,
                        "override_config": None,
                        "last_updated": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"✓ Signal override cleared at {location_id}")
            
        except Exception as e:
            logger.error(f"Failed to clear signal override: {e}")
    
    def get_active_overrides(self) -> List[Dict]:
        """Get list of currently active emergency overrides"""
        return [
            {
                "override_id": override_id,
                **override_data
            }
            for override_id, override_data in self.active_overrides.items()
        ]
    
    async def manual_clear_override(self, override_id: str) -> bool:
        """
        Manually clear an emergency override
        
        Args:
            override_id: Override identifier
            
        Returns:
            True if cleared successfully
        """
        if override_id not in self.active_overrides:
            return False
        
        override_data = self.active_overrides[override_id]
        await self._clear_signal_override(override_data["location_id"])
        del self.active_overrides[override_id]
        
        logger.info(f"✓ Emergency override manually cleared: {override_id}")
        return True
