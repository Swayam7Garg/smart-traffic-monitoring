"""
Violations and alerts API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.violations import Violation, Alert, ViolationType, AlertType
from ..database import get_violations_collection

router = APIRouter()


@router.get("/", response_model=List[Violation])
async def get_violations(
    location_id: Optional[str] = None,
    violation_type: Optional[ViolationType] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Get traffic violations"""
    collection = await get_violations_collection()
    
    query = {}
    if location_id:
        query["location_id"] = location_id
    if violation_type:
        query["violation_type"] = violation_type
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    violations = await cursor.to_list(length=limit)
    
    return [Violation(**v) for v in violations]


@router.post("/", response_model=Violation)
async def report_violation(violation: Violation):
    """Report a new traffic violation"""
    collection = await get_violations_collection()
    
    violation_dict = violation.model_dump()
    result = await collection.insert_one(violation_dict)
    
    violation_dict["violation_id"] = str(result.inserted_id)
    return Violation(**violation_dict)


@router.get("/stats")
async def get_violation_stats(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get violation statistics"""
    collection = await get_violations_collection()
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_time}}},
        {
            "$group": {
                "_id": "$violation_type",
                "count": {"$sum": 1},
                "avg_severity": {"$avg": "$severity"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    cursor = collection.aggregate(pipeline)
    stats = await cursor.to_list(length=20)
    
    total_violations = await collection.count_documents({
        "timestamp": {"$gte": start_time}
    })
    
    return {
        "time_range_hours": hours,
        "total_violations": total_violations,
        "by_type": stats
    }


@router.get("/recent", response_model=List[Violation])
async def get_recent_violations(minutes: int = Query(30, ge=1, le=1440)):
    """Get recent violations"""
    collection = await get_violations_collection()
    
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
    cursor = collection.find({
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1)
    
    violations = await cursor.to_list(length=100)
    return [Violation(**v) for v in violations]


# Alert endpoints
@router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    resolved: Optional[bool] = None,
    alert_type: Optional[AlertType] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get system alerts"""
    # Note: Alerts would typically be in a separate collection
    # For now, returning mock structure
    return []


@router.post("/alerts", response_model=Alert)
async def create_alert(alert: Alert):
    """Create a new system alert"""
    # Implementation would store alert in database
    return alert


@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    return {"message": f"Alert {alert_id} marked as resolved"}
