"""
Traffic data API endpoints
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.traffic import TrafficData, TrafficSummary, VehicleDetection
from ..database import get_traffic_collection
from ..ml.detection_storage import (
    get_detection_history,
    get_emergency_vehicle_history,
    get_detection_statistics
)
import uuid
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (will be initialized in main.py)
video_processor = None
detector = None
analyzer = None
emergency_system = None


@router.get("/current", response_model=List[TrafficData])
async def get_current_traffic(
    location_id: Optional[str] = Query(None, description="Filter by location")
):
    """Get current real-time traffic data"""
    collection = await get_traffic_collection()
    
    # Get data from last 5 minutes
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    query = {"timestamp": {"$gte": five_min_ago}}
    
    if location_id:
        query["location_id"] = location_id
    
    cursor = collection.find(query).sort("timestamp", -1)
    traffic_data = await cursor.to_list(length=100)
    
    return [TrafficData(**data) for data in traffic_data]


@router.post("/report", response_model=TrafficData)
async def report_traffic_data(traffic_data: TrafficData):
    """Submit new traffic data"""
    collection = await get_traffic_collection()
    
    data_dict = traffic_data.model_dump()
    result = await collection.insert_one(data_dict)
    
    data_dict["_id"] = str(result.inserted_id)
    return TrafficData(**data_dict)


@router.get("/summary/{location_id}", response_model=TrafficSummary)
async def get_traffic_summary(
    location_id: str,
    period: str = Query("hourly", regex="^(hourly|daily|weekly)$")
):
    """Get traffic summary for a location"""
    collection = await get_traffic_collection()
    
    # Calculate time range based on period
    now = datetime.utcnow()
    if period == "hourly":
        start_time = now - timedelta(hours=1)
    elif period == "daily":
        start_time = now - timedelta(days=1)
    else:  # weekly
        start_time = now - timedelta(weeks=1)
    
    # Aggregate traffic data
    pipeline = [
        {
            "$match": {
                "location_id": location_id,
                "timestamp": {"$gte": start_time}
            }
        },
        {
            "$group": {
                "_id": "$location_id",
                "total_vehicles": {"$sum": "$vehicle_count"},
                "avg_congestion": {"$avg": "$congestion_level"}
            }
        }
    ]
    
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    if not results:
        raise HTTPException(status_code=404, detail="No data found for location")
    
    data = results[0]
    return TrafficSummary(
        location_id=location_id,
        time_period=period,
        total_vehicles=data.get("total_vehicles", 0),
        average_congestion=data.get("avg_congestion", 0),
        vehicle_distribution={}
    )


@router.get("/history/{location_id}")
async def get_traffic_history(
    location_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve")
):
    """Get historical traffic data"""
    collection = await get_traffic_collection()
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    cursor = collection.find({
        "location_id": location_id,
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", 1)
    
    history = await cursor.to_list(length=1000)
    return {"location_id": location_id, "data": history}


# Video Processing Endpoints

@router.post("/upload-video")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    location_id: str = Query("unknown", description="Location identifier")
):
    """
    Upload traffic video for processing
    
    Returns job_id for tracking progress
    """
    if not video_processor:
        raise HTTPException(status_code=503, detail="Video processor not initialized")
    
    # Validate file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: mp4, avi, mov, mkv")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file (OPTIMIZED: larger buffer for faster upload)
    upload_dir = Path("./data/videos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{job_id}_{file.filename}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 🔥 ITERATION #8: Define immediate emergency callback
    async def emergency_alert_callback(emergency_data: Dict):
        """
        Immediate emergency vehicle detection callback
        Triggers signal override and WebSocket broadcast WITHOUT waiting for video completion
        """
        try:
            logger.critical(f"🚨 IMMEDIATE EMERGENCY ALERT: {emergency_data}")
            
            # Trigger emergency priority system immediately
            if emergency_system:
                direction = "north"  # Default, could be detected from video metadata
                response = await emergency_system.handle_emergency_detection(
                    location_id=emergency_data["location_id"],
                    direction=direction,
                    emergency_vehicles=emergency_data["emergency_vehicles"]
                )
                logger.info(f"✓ Emergency signal override activated: {response}")
            
            # Broadcast emergency alert via WebSocket
            from ..main import manager
            await manager.broadcast({
                "type": "emergency_alert",
                "priority": "CRITICAL",
                "location_id": emergency_data["location_id"],
                "frame_number": emergency_data["frame_number"],
                "timestamp": emergency_data["detected_at"],
                "emergency_vehicles": emergency_data["emergency_vehicles"],
                "message": "🚨 EMERGENCY VEHICLE DETECTED - Signal override activated",
                "signal_state": "GREEN_ACTIVATED"
            })
            logger.info("✓ Emergency WebSocket broadcast sent")
            
        except Exception as e:
            logger.error(f"Emergency callback error: {e}")
    
    # Start processing in background with emergency callback
    background_tasks.add_task(
        video_processor.process_video_async,
        str(file_path),
        job_id,
        location_id,
        True,
        emergency_alert_callback  # Pass the immediate callback
    )
    
    return {
        "job_id": job_id,
        "filename": file.filename,
        "location_id": location_id,
        "status": "queued",
        "message": "Video uploaded successfully. Processing started."
    }


@router.get("/processing-status/{job_id}")
async def get_processing_status(job_id: str):
    """Get video processing status"""
    if not video_processor:
        raise HTTPException(status_code=503, detail="Video processor not initialized")
    
    status = video_processor.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status


@router.get("/detection-results/{job_id}")
async def get_detection_results(job_id: str):
    """Get detailed detection results for processed video"""
    if not video_processor:
        raise HTTPException(status_code=503, detail="Video processor not initialized")
    
    job = video_processor.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        return {
            "status": job["status"],
            "message": f"Processing {job['status']}"
        }
    
    return job.get("results", {})


@router.get("/recent-jobs")
async def get_recent_video_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of recent jobs to return")
):
    """Get recent video processing jobs from database"""
    from ..database import Database
    
    db = Database.get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    collection = db.video_processing_jobs
    
    # Get recent jobs sorted by processed time
    cursor = collection.find({}).sort("processed_at", -1).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string and format response
    result = []
    for job in jobs:
        job['_id'] = str(job['_id'])
        
        # Handle both nested and flat data structures
        detections = job.get('detections', {})
        analysis = job.get('analysis', {})
        
        # Try nested structure first, fall back to flat if not found
        vehicle_count = detections.get('total_vehicles', job.get('vehicle_count', 0))
        vehicle_types = detections.get('vehicle_types', job.get('vehicle_types', {}))
        emergency_count = detections.get('emergency_vehicles', job.get('emergency_vehicles', 0))
        congestion = analysis.get('peak_congestion', analysis.get('avg_congestion', job.get('congestion_level', 0)))
        
        result.append({
            'id': job.get('job_id'),
            'location_id': job.get('location_id'),
            'status': job.get('status'),
            'timestamp': job.get('processed_at').isoformat() if job.get('processed_at') else None,
            'vehicle_count': vehicle_count,
            'vehicle_types': vehicle_types,
            'emergency_vehicles': emergency_count,
            'congestion_level': congestion,
            'output_video': job.get('output_video'),
            'frames': job.get('frames', {})
        })
    
    return result


@router.get("/download-processed-video/{job_id}")
async def download_processed_video(job_id: str):
    """Download processed video with annotations"""
    from fastapi.responses import FileResponse
    import os
    
    if not video_processor:
        raise HTTPException(status_code=503, detail="Video processor not initialized")
    
    job = video_processor.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Video processing not complete. Status: {job['status']}")
    
    results = job.get("results", {})
    output_video = results.get("output_video")
    
    if not output_video:
        raise HTTPException(status_code=404, detail="No output video path in job results. Video may not have been saved.")
    
    # Convert to absolute path if relative
    video_path = Path(output_video)
    if not video_path.is_absolute():
        # Try relative to backend directory
        backend_dir = Path(__file__).parent.parent.parent
        video_path = backend_dir / output_video
    
    if not video_path.exists():
        # Try alternative path - relative to current working directory
        video_path = Path(os.getcwd()) / output_video
        
    if not video_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Processed video file not found at: {output_video}. The file may have been deleted after server restart."
        )
    
    return FileResponse(
        str(video_path),
        media_type="video/mp4",
        filename=f"processed_{job_id}.mp4"
    )


@router.post("/process-realtime")
async def process_realtime_frame(
    location_id: str = Query(..., description="Location identifier"),
    direction: str = Query("north", description="Direction of traffic flow"),
    frame_data: bytes = File(..., description="Frame image data")
):
    """
    Process a single frame for real-time detection
    
    Used for live camera feeds. Automatically triggers emergency priority if detected.
    """
    if not detector or not analyzer:
        raise HTTPException(status_code=503, detail="Detection system not initialized")
    
    import cv2
    import numpy as np
    
    # Decode frame
    nparr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image data")
    
    # Detect vehicles
    detections = detector.detect(frame, detect_three_wheelers=True)
    
    # Analyze traffic
    analysis = analyzer.analyze_frame(detections)
    
    # Check for emergency vehicles
    emergency_detected = detector.has_emergency_vehicles(detections)
    emergency_vehicles = detector.get_emergency_vehicles(detections) if emergency_detected else []
    
    # Trigger emergency priority if detected
    emergency_override = None
    if emergency_detected and emergency_system:
        emergency_override = await emergency_system.handle_emergency_detection(
            location_id=location_id,
            direction=direction,
            emergency_vehicles=emergency_vehicles
        )
    
    return {
        "location_id": location_id,
        "timestamp": datetime.utcnow().isoformat(),
        "vehicle_count": analysis["vehicle_count"],
        "vehicle_types": analysis["vehicle_types"],
        "congestion_level": analysis["congestion_level"],
        "traffic_state": analysis["traffic_state"],
        "emergency_detected": emergency_detected,
        "emergency_vehicles": emergency_vehicles,
        "emergency_override": emergency_override,
        "detections": detections
    }


# Emergency Priority Endpoints

@router.get("/emergency/active")
async def get_active_emergencies():
    """Get all active emergency overrides"""
    if not emergency_system:
        raise HTTPException(status_code=503, detail="Emergency system not initialized")
    
    overrides = emergency_system.get_active_overrides()
    return {
        "active_count": len(overrides),
        "overrides": overrides
    }


@router.post("/emergency/clear/{override_id}")
async def clear_emergency_override(override_id: str):
    """Manually clear an emergency override"""
    if not emergency_system:
        raise HTTPException(status_code=503, detail="Emergency system not initialized")
    
    success = await emergency_system.manual_clear_override(override_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Override not found")
    
    return {
        "message": "Emergency override cleared successfully",
        "override_id": override_id
    }


@router.post("/emergency/check-expired")
async def check_expired_overrides():
    """Check and clear expired emergency overrides"""
    if not emergency_system:
        raise HTTPException(status_code=503, detail="Emergency system not initialized")
    
    cleared_count = await emergency_system.check_expired_overrides()
    
    return {
        "message": f"Cleared {cleared_count} expired overrides",
        "cleared": cleared_count
    }


@router.get("/detection-history/{location_id}", response_model=List[Dict[str, Any]])
async def get_location_detection_history(
    location_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history (max 7 days)"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type")
):
    """Get detection history for a location"""
    detections = await get_detection_history(location_id, hours, vehicle_type)
    return detections


@router.get("/detection-statistics/{location_id}")
async def get_location_statistics(
    location_id: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history")
):
    """Get detection statistics for a location"""
    stats = await get_detection_statistics(location_id, hours)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No data found for location")
    
    return stats


@router.get("/emergency-history")
async def get_emergency_history(
    location_id: Optional[str] = Query(None, description="Filter by location"),
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history")
):
    """Get emergency vehicle detection history"""
    emergencies = await get_emergency_vehicle_history(location_id, hours)
    
    return {
        "total": len(emergencies),
        "emergencies": emergencies
    }
