from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime

from ..database import Database
from ..models.settings import (
    SignalTiming, SignalTimingUpdate,
    Location, LocationCreate, LocationUpdate,
    DetectionConfig, DetectionConfigUpdate,
    SystemSettings, SystemSettingsUpdate
)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

# Signal Timing Endpoints
@router.get("/signal-timings", response_model=List[SignalTiming])
async def get_signal_timings():
    """Get all signal timing configurations"""
    db = Database.get_database()
    timings = await db.signal_timings.find().to_list(100)
    
    # If no timings exist, return default configurations
    if not timings:
        default_timings = [
            {
                "location_id": "junction_01",
                "location_name": "Main Junction",
                "vehicle_type": "car",
                "green_duration": 45,
                "red_duration": 30,
                "time_period": "peak",
                "updated_at": datetime.now()
            },
            {
                "location_id": "junction_01",
                "location_name": "Main Junction",
                "vehicle_type": "bike",
                "green_duration": 30,
                "red_duration": 45,
                "time_period": "peak",
                "updated_at": datetime.now()
            },
            {
                "location_id": "junction_01",
                "location_name": "Main Junction",
                "vehicle_type": "car",
                "green_duration": 30,
                "red_duration": 30,
                "time_period": "normal",
                "updated_at": datetime.now()
            },
            {
                "location_id": "junction_01",
                "location_name": "Main Junction",
                "vehicle_type": "bike",
                "green_duration": 25,
                "red_duration": 35,
                "time_period": "normal",
                "updated_at": datetime.now()
            },
            {
                "location_id": "junction_01",
                "location_name": "Main Junction",
                "vehicle_type": "car",
                "green_duration": 20,
                "red_duration": 20,
                "time_period": "night",
                "updated_at": datetime.now()
            }
        ]
        # Insert defaults
        await db.signal_timings.insert_many(default_timings)
        timings = default_timings
    
    return timings

@router.put("/signal-timings")
async def update_signal_timings(
    timings: List[SignalTiming]
):
    """Update all signal timing configurations"""
    db = Database.get_database()
    # Delete existing timings
    await db.signal_timings.delete_many({})
    
    # Insert new timings
    timing_docs = []
    for timing in timings:
        doc = timing.dict()
        doc["updated_at"] = datetime.now()
        timing_docs.append(doc)
    
    if timing_docs:
        await db.signal_timings.insert_many(timing_docs)
    
    return {"message": "Signal timings updated successfully", "count": len(timing_docs)}

@router.put("/signal-timings/{location_id}/{vehicle_type}/{time_period}")
async def update_signal_timing(
    location_id: str,
    vehicle_type: str,
    time_period: str,
    update: SignalTimingUpdate
):
    """Update a specific signal timing configuration"""
    db = Database.get_database()
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    result = await db.signal_timings.update_one(
        {
            "location_id": location_id,
            "vehicle_type": vehicle_type,
            "time_period": time_period
        },
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Signal timing not found")
    
    return {"message": "Signal timing updated successfully"}

# Location Endpoints
@router.get("/locations", response_model=List[Location])
async def get_locations():
    """Get all monitoring locations"""
    db = Database.get_database()
    locations = await db.locations.find().to_list(100)
    
    # If no locations exist, return default locations
    if not locations:
        default_locations = [
            {
                "id": "junction_01",
                "name": "Main Junction",
                "latitude": 28.7041,
                "longitude": 77.1025,
                "camera_id": "CAM001",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "junction_02",
                "name": "Market Square",
                "latitude": 28.7051,
                "longitude": 77.1035,
                "camera_id": "CAM002",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        await db.locations.insert_many(default_locations)
        locations = default_locations
    
    return locations

@router.post("/locations", response_model=Location)
async def create_location(
    location: LocationCreate
):
    """Create a new monitoring location"""
    db = Database.get_database()
    # Generate location ID
    location_id = f"junction_{int(datetime.now().timestamp())}"
    
    location_doc = location.dict()
    location_doc["id"] = location_id
    location_doc["created_at"] = datetime.now()
    location_doc["updated_at"] = datetime.now()
    
    await db.locations.insert_one(location_doc)
    
    return location_doc

@router.put("/locations/{location_id}")
async def update_location(
    location_id: str,
    update: LocationUpdate
):
    """Update a monitoring location"""
    db = Database.get_database()
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    result = await db.locations.update_one(
        {"id": location_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {"message": "Location updated successfully"}

@router.delete("/locations/{location_id}")
async def delete_location(
    location_id: str
):
    """Delete a monitoring location"""
    db = Database.get_database()
    result = await db.locations.delete_one({"id": location_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {"message": "Location deleted successfully"}

# Detection Configuration Endpoints
@router.get("/detection-config", response_model=DetectionConfig)
async def get_detection_config():
    """Get detection configuration"""
    db = Database.get_database()
    config = await db.detection_config.find_one({"_id": "default"})
    
    # If no config exists, return current defaults
    if not config:
        default_config = {
            "_id": "default",
            "confidence_threshold": 0.2,
            "iou_threshold": 0.4,
            "emergency_color_threshold": 50,
            "autorickshaw_size_threshold": 25000,
            "frame_skip": 2,
            "updated_at": datetime.now()
        }
        await db.detection_config.insert_one(default_config)
        config = default_config
    
    return config

@router.put("/detection-config")
async def update_detection_config(
    update: DetectionConfigUpdate
):
    """Update detection configuration"""
    db = Database.get_database()
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    result = await db.detection_config.update_one(
        {"_id": "default"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Detection configuration updated successfully", "updated": update_data}

@router.post("/detection-config/reset")
async def reset_detection_config():
    """Reset detection configuration to defaults"""
    db = Database.get_database()
    default_config = {
        "_id": "default",
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45,
        "emergency_color_threshold": 50,
        "autorickshaw_size_threshold": 25000,
        "frame_skip": 2,
        "updated_at": datetime.now()
    }
    
    await db.detection_config.replace_one(
        {"_id": "default"},
        default_config,
        upsert=True
    )
    
    return {"message": "Detection configuration reset to defaults", "config": default_config}

# System Settings Endpoints
@router.get("/system", response_model=SystemSettings)
async def get_system_settings():
    """Get system settings"""
    db = Database.get_database()
    settings = await db.system_settings.find_one({"_id": "default"})
    
    # If no settings exist, return defaults
    if not settings:
        default_settings = {
            "_id": "default",
            "auto_refresh_interval": 5000,
            "max_video_size_mb": 500,
            "enable_notifications": True,
            "dark_mode": False,
            "language": "en",
            "updated_at": datetime.now()
        }
        await db.system_settings.insert_one(default_settings)
        settings = default_settings
    
    return settings

@router.put("/system")
async def update_system_settings(
    update: SystemSettingsUpdate
):
    """Update system settings"""
    db = Database.get_database()
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    result = await db.system_settings.update_one(
        {"_id": "default"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "System settings updated successfully", "updated": update_data}

@router.post("/system/reset")
async def reset_system_settings():
    """Reset system settings to defaults"""
    db = Database.get_database()
    default_settings = {
        "_id": "default",
        "auto_refresh_interval": 5000,
        "max_video_size_mb": 500,
        "enable_notifications": True,
        "dark_mode": False,
        "language": "en",
        "updated_at": datetime.now()
    }
    
    await db.system_settings.replace_one(
        {"_id": "default"},
        default_settings,
        upsert=True
    )
    
    return {"message": "System settings reset to defaults", "settings": default_settings}
