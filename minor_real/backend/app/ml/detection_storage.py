"""
Detection storage models and database operations
"""

from typing import List, Dict, Optional
from datetime import datetime
from ..database import Database
import logging

logger = logging.getLogger(__name__)


async def store_detection_batch(
    location_id: str,
    detections: List[Dict],
    timestamp: Optional[datetime] = None
) -> bool:
    """
    Store a batch of vehicle detections to MongoDB
    
    Args:
        location_id: Location identifier
        detections: List of detection dictionaries
        timestamp: Detection timestamp (default: now)
        
    Returns:
        True if stored successfully
    """
    if not detections:
        return True
    
    try:
        db = Database.get_database()
        if db is None:
            logger.debug("Database not available - skipping detection storage")
            return False
        collection = db.vehicle_detections
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Prepare documents
        documents = []
        for detection in detections:
            doc = {
                "location_id": location_id,
                "timestamp": timestamp,
                "vehicle_type": detection.get("class_name"),
                "confidence": detection.get("confidence"),
                "bbox": detection.get("bbox"),
                "track_id": detection.get("track_id"),
                "is_emergency": detection.get("is_emergency", False)
            }
            documents.append(doc)
        
        # Bulk insert
        result = await collection.insert_many(documents)
        logger.debug(f"Stored {len(result.inserted_ids)} detections")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to store detections: {e}")
        return False


async def store_video_processing_job(
    job_id: str,
    video_path: str,
    location_id: str,
    results: Dict
) -> bool:
    """
    Store video processing job results and create traffic data for analytics
    
    Args:
        job_id: Unique job identifier
        video_path: Path to video file
        location_id: Location identifier
        results: Processing results dictionary
        
    Returns:
        True if stored successfully
    """
    try:
        db = Database.get_database()
        jobs_collection = db.video_processing_jobs
        traffic_collection = db.traffic_data
        
        timestamp = datetime.utcnow()
        
        # Store video processing job
        document = {
            "job_id": job_id,
            "video_path": video_path,
            "location_id": location_id,
            "status": results.get("status", "completed"),
            "processed_at": timestamp,
            "frames": results.get("frames", {}),
            "detections": results.get("detections", {}),
            "analysis": results.get("analysis", {}),
            "emergency_alerts": results.get("emergency_alerts", []),
            "output_video": results.get("output_video")
        }
        
        await jobs_collection.insert_one(document)
        logger.info(f"✓ Video job {job_id} stored in database")
        
        # Create traffic data entry for analytics
        detections = results.get("detections", {})
        analysis = results.get("analysis", {})
        vehicle_counts = detections.get("vehicle_types", {})
        
        traffic_document = {
            "location_id": location_id,
            "timestamp": timestamp,
            "vehicle_count": detections.get("total_vehicles", 0),
            "vehicle_counts": vehicle_counts,
            "congestion_level": analysis.get("peak_congestion", 0),
            "average_congestion": analysis.get("avg_congestion", 0),
            "emergency_vehicles": detections.get("emergency_vehicles", 0),
            "source": "video_processing",
            "job_id": job_id
        }
        
        await traffic_collection.insert_one(traffic_document)
        logger.info(f"✓ Traffic data created for analytics dashboard")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to store video job: {e}")
        return False


async def get_detection_history(
    location_id: str,
    hours: int = 24,
    vehicle_type: Optional[str] = None
) -> List[Dict]:
    """
    Retrieve detection history for a location
    
    Args:
        location_id: Location identifier
        hours: Hours of history to retrieve
        vehicle_type: Filter by vehicle type (optional)
        
    Returns:
        List of detection records
    """
    try:
        db = Database.get_database()
        collection = db.vehicle_detections
        
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = {
            "location_id": location_id,
            "timestamp": {"$gte": cutoff}
        }
        
        if vehicle_type:
            query["vehicle_type"] = vehicle_type
        
        cursor = collection.find(query).sort("timestamp", -1)
        detections = await cursor.to_list(length=1000)
        
        return detections
        
    except Exception as e:
        logger.error(f"Failed to retrieve detection history: {e}")
        return []


async def get_emergency_vehicle_history(
    location_id: Optional[str] = None,
    hours: int = 24
) -> List[Dict]:
    """
    Retrieve emergency vehicle detection history
    
    Args:
        location_id: Location identifier (optional)
        hours: Hours of history to retrieve
        
    Returns:
        List of emergency detection records
    """
    try:
        db = Database.get_database()
        collection = db.vehicle_detections
        
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = {
            "is_emergency": True,
            "timestamp": {"$gte": cutoff}
        }
        
        if location_id:
            query["location_id"] = location_id
        
        cursor = collection.find(query).sort("timestamp", -1)
        emergencies = await cursor.to_list(length=500)
        
        return emergencies
        
    except Exception as e:
        logger.error(f"Failed to retrieve emergency history: {e}")
        return []


async def get_detection_statistics(
    location_id: str,
    hours: int = 24
) -> Dict:
    """
    Get detection statistics for a location
    
    Args:
        location_id: Location identifier
        hours: Hours of history to analyze
        
    Returns:
        Statistics dictionary
    """
    try:
        db = Database.get_database()
        collection = db.vehicle_detections
        
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {
                "$match": {
                    "location_id": location_id,
                    "timestamp": {"$gte": cutoff}
                }
            },
            {
                "$group": {
                    "_id": "$vehicle_type",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"}
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        
        # Count emergencies
        emergency_count = await collection.count_documents({
            "location_id": location_id,
            "timestamp": {"$gte": cutoff},
            "is_emergency": True
        })
        
        stats = {
            "location_id": location_id,
            "time_range_hours": hours,
            "vehicle_types": {r["_id"]: r["count"] for r in results},
            "total_vehicles": sum(r["count"] for r in results),
            "emergency_vehicles": emergency_count
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get detection statistics: {e}")
        return {}
