"""
Camera management API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import logging

from ..models.cameras import (
    Camera, CameraCreate, CameraUpdate, StreamControl, LiveDetectionData
)
from ..database import Database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cameras", response_model=List[Camera])
async def get_cameras():
    """Get all registered cameras"""
    db = Database.get_database()
    cameras = await db.cameras.find().to_list(length=None)
    return cameras


@router.get("/cameras/{camera_id}", response_model=Camera)
async def get_camera(camera_id: str):
    """Get specific camera by ID"""
    db = Database.get_database()
    camera = await db.cameras.find_one({"camera_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/cameras", response_model=Camera, status_code=status.HTTP_201_CREATED)
async def create_camera(camera: CameraCreate):
    """Register a new camera"""
    db = Database.get_database()
    
    # Check if camera already exists
    existing = await db.cameras.find_one({"camera_id": camera.camera_id})
    if existing:
        raise HTTPException(status_code=400, detail="Camera ID already exists")
    
    # Create camera document
    camera_doc = {
        **camera.model_dump(),
        "status": "inactive",
        "is_streaming": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "last_active": None
    }
    
    await db.cameras.insert_one(camera_doc)
    logger.info(f"Created camera: {camera.camera_id}")
    return camera_doc


@router.put("/cameras/{camera_id}", response_model=Camera)
async def update_camera(camera_id: str, updates: CameraUpdate):
    """Update camera configuration"""
    db = Database.get_database()
    
    camera = await db.cameras.find_one({"camera_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Only update provided fields
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    await db.cameras.update_one(
        {"camera_id": camera_id},
        {"$set": update_data}
    )
    
    updated_camera = await db.cameras.find_one({"camera_id": camera_id})
    logger.info(f"Updated camera: {camera_id}")
    return updated_camera


@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: str):
    """Delete camera (only if not streaming)"""
    db = Database.get_database()
    
    camera = await db.cameras.find_one({"camera_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if camera.get("is_streaming"):
        raise HTTPException(status_code=400, detail="Cannot delete camera while streaming. Stop stream first.")
    
    await db.cameras.delete_one({"camera_id": camera_id})
    logger.info(f"Deleted camera: {camera_id}")
    return {"message": "Camera deleted successfully"}


# Global stream processor instance
_stream_processor = None

@router.post("/cameras/{camera_id}/stream")
async def control_stream(camera_id: str, action: str):
    """
    Start or stop camera stream
    
    Args:
        camera_id: Camera identifier
        action: 'start' or 'stop'
    """
    from ..ml.video_processor import LiveStreamProcessor
    from ..ml.detector import VehicleDetector
    from ..ml.traffic_analyzer import TrafficAnalyzer
    from ..config import get_settings
    from pathlib import Path
    import base64
    import cv2
    
    global _stream_processor
    
    settings = get_settings()
    db = Database.get_database()
    
    # Get camera
    camera = await db.cameras.find_one({"camera_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if action == "start":
        if camera.get("is_streaming"):
            raise HTTPException(status_code=400, detail="Stream already active")
        
        # Get paths relative to backend directory
        backend_dir = Path(__file__).parent.parent.parent
        model_path = backend_dir / "data" / "models" / "yolov8n.pt"
        
        # Initialize live stream processor (reuse global instance)
        if _stream_processor is None:
            detector = VehicleDetector(
                model_path=str(model_path),
                confidence=settings.YOLO_CONFIDENCE
            )
            analyzer = TrafficAnalyzer()
            _stream_processor = LiveStreamProcessor(detector, analyzer)
        
        processor = _stream_processor
        
        # Callback to store detections in DB and broadcast via WebSocket
        async def detection_callback(data):
            """Store live detection data and broadcast to WebSocket clients"""
            # Encode frame to base64 for WebSocket transmission
            frame = data.get('frame')
            frame_base64 = None
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            detection_doc = {
                "camera_id": camera_id,
                "stream_id": data["stream_id"],
                "location_id": data["location_id"],
                "timestamp": datetime.now(),
                "vehicle_counts": data["analysis"].get("vehicle_types", {}),
                "congestion_level": data["analysis"].get("congestion_level", 0),
                "average_speed": data["analysis"].get("avg_vehicle_count", 0),
                "emergency_vehicles": [
                    det for det in data["detections"] 
                    if det.get("is_emergency")
                ],
                "total_detections": len(data["detections"])
            }
            await db.live_detections.insert_one(detection_doc)
            
            # Determine direction based on camera name or assign automatically
            direction = "north"  # Default
            camera_name = camera.get("name", "").lower()
            if "north" in camera_name or "n" == camera_name:
                direction = "north"
            elif "south" in camera_name or "s" == camera_name:
                direction = "south"
            elif "east" in camera_name or "e" == camera_name:
                direction = "east"
            elif "west" in camera_name or "w" == camera_name:
                direction = "west"
            
            # Broadcast to WebSocket clients with frame
            from ..main import manager
            await manager.broadcast_json({
                "camera_id": camera_id,
                "stream_id": data["stream_id"],
                "direction": direction,
                "timestamp": data["timestamp"],
                "detections": data["detections"],
                "analysis": data["analysis"],
                "frame": frame_base64
            })
            
            logger.debug(f"Stored and broadcasted live detection for {camera_id}")
        
        # Start stream processing in background
        import asyncio
        stream_id = f"stream_{camera_id}_{int(datetime.now().timestamp())}"
        asyncio.create_task(
            processor.process_stream(
                stream_url=camera["rtsp_url"],
                stream_id=stream_id,
                location_id=camera["location_id"],
                callback=detection_callback
            )
        )
        
        # Update camera status
        await db.cameras.update_one(
            {"camera_id": camera_id},
            {"$set": {
                "is_streaming": True,
                "status": "active",
                "last_active": datetime.now(),
                "stream_id": stream_id
            }}
        )
        
        logger.info(f"Started stream for camera: {camera_id}")
        return {"message": "Stream started", "stream_id": stream_id}
    
    elif action == "stop":
        if not camera.get("is_streaming"):
            raise HTTPException(status_code=400, detail="Stream not active")
        
        # Stop stream using global processor
        stream_id = camera.get("stream_id")
        if stream_id and _stream_processor:
            _stream_processor.stop_stream(stream_id)
        
        # Update camera status
        await db.cameras.update_one(
            {"camera_id": camera_id},
            {"$set": {
                "is_streaming": False,
                "status": "inactive"
            }}
        )
        
        logger.info(f"Stopped stream for camera: {camera_id}")
        return {"message": "Stream stopped"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'start' or 'stop'")


@router.get("/cameras/{camera_id}/live-data")
async def get_live_data(camera_id: str, limit: int = 10):
    """Get recent live detection data for a camera"""
    db = Database.get_database()
    
    # Get recent detections
    detections = await db.live_detections.find(
        {"camera_id": camera_id}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    return detections


@router.get("/streams/active")
async def get_active_streams():
    """Get all currently active camera streams"""
    db = Database.get_database()
    active_cameras = await db.cameras.find({"is_streaming": True}).to_list(length=None)
    return active_cameras
