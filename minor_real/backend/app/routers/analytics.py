"""
Analytics and reporting API endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import io
import csv
from ..database import get_traffic_collection, get_violations_collection

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get dashboard statistics"""
    try:
        traffic_col = await get_traffic_collection()
        violations_col = await get_violations_collection()
        
        if not traffic_col or not violations_col:
            # Return empty stats if collections don't exist
            return {
                "time_range_hours": hours,
                "total_vehicles": 0,
                "average_congestion": 0,
                "total_violations": 0,
                "monitored_locations": 0,
                "timestamp": datetime.utcnow()
            }
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get traffic statistics
        traffic_pipeline = [
            {"$match": {"timestamp": {"$gte": start_time}}},
            {
                "$group": {
                    "_id": None,
                    "total_vehicles": {"$sum": "$vehicle_count"},
                    "avg_congestion": {"$avg": "$congestion_level"},
                    "locations": {"$addToSet": "$location_id"}
                }
            }
        ]
        
        traffic_cursor = traffic_col.aggregate(traffic_pipeline)
        traffic_stats = await traffic_cursor.to_list(length=1)
        
        # Get violations count
        violations_count = await violations_col.count_documents({
            "timestamp": {"$gte": start_time}
        })
        
        # Combine statistics
        stats = traffic_stats[0] if traffic_stats else {}
        
        return {
            "time_range_hours": hours,
            "total_vehicles": stats.get("total_vehicles", 0),
            "average_congestion": round(stats.get("avg_congestion", 0), 2),
            "total_violations": violations_count,
            "monitored_locations": len(stats.get("locations", [])),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        # Return empty stats on any error
        return {
            "time_range_hours": hours,
            "total_vehicles": 0,
            "average_congestion": 0,
            "total_violations": 0,
            "monitored_locations": 0,
            "timestamp": datetime.utcnow()
        }


@router.get("/trends/{location_id}")
async def get_traffic_trends(
    location_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days for trend analysis")
):
    """Get traffic trends over time"""
    collection = await get_traffic_collection()
    
    start_time = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "location_id": location_id,
                "timestamp": {"$gte": start_time}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"},
                    "hour": {"$hour": "$timestamp"}
                },
                "avg_vehicles": {"$avg": "$vehicle_count"},
                "avg_congestion": {"$avg": "$congestion_level"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    cursor = collection.aggregate(pipeline)
    trends = await cursor.to_list(length=1000)
    
    return {
        "location_id": location_id,
        "period_days": days,
        "trends": trends
    }


@router.get("/peak-hours/{location_id}")
async def get_peak_hours(location_id: str):
    """Get peak traffic hours for a location"""
    collection = await get_traffic_collection()
    
    # Get last 7 days
    start_time = datetime.utcnow() - timedelta(days=7)
    
    pipeline = [
        {
            "$match": {
                "location_id": location_id,
                "timestamp": {"$gte": start_time}
            }
        },
        {
            "$group": {
                "_id": {"$hour": "$timestamp"},
                "avg_vehicles": {"$avg": "$vehicle_count"},
                "avg_congestion": {"$avg": "$congestion_level"}
            }
        },
        {"$sort": {"avg_vehicles": -1}}
    ]
    
    cursor = collection.aggregate(pipeline)
    hourly_stats = await cursor.to_list(length=24)
    
    return {
        "location_id": location_id,
        "peak_hours": hourly_stats[:5],  # Top 5 peak hours
        "hourly_breakdown": hourly_stats
    }


@router.get("/report")
async def generate_report(
    location_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Generate comprehensive traffic report"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    collection = await get_traffic_collection()
    
    query = {"timestamp": {"$gte": start_date, "$lte": end_date}}
    if location_id:
        query["location_id"] = location_id
    
    # Get summary statistics
    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$location_id",
                "total_vehicles": {"$sum": "$vehicle_count"},
                "avg_congestion": {"$avg": "$congestion_level"},
                "max_congestion": {"$max": "$congestion_level"},
                "data_points": {"$sum": 1}
            }
        }
    ]
    
    cursor = collection.aggregate(pipeline)
    report_data = await cursor.to_list(length=100)
    
    return {
        "report_period": {
            "start": start_date,
            "end": end_date
        },
        "locations": report_data,
        "generated_at": datetime.utcnow()
    }


@router.get("/overview")
async def get_analytics_overview(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get comprehensive analytics overview with charts data"""
    collection = await get_traffic_collection()
    
    # Parse dates or use defaults
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    else:
        start = datetime.utcnow() - timedelta(days=7)
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        end = datetime.utcnow()
    
    query = {"timestamp": {"$gte": start, "$lte": end}}
    
    # Get all traffic data
    cursor = collection.find(query).sort("timestamp", 1)
    traffic_data = await cursor.to_list(length=1000)
    
    if not traffic_data:
        return {
            "summary": {
                "total_vehicles": 0,
                "total_videos": 0,
                "avg_vehicles_per_video": 0,
                "emergency_detections": 0
            },
            "vehicle_distribution": {},
            "timeline_data": [],
            "peak_hours": [],
            "location_stats": []
        }
    
    # Calculate summary statistics
    total_vehicles = sum(item.get("vehicle_count", 0) for item in traffic_data)
    total_videos = len(traffic_data)
    emergency_count = sum(item.get("emergency_vehicles", 0) for item in traffic_data)
    
    # Aggregate vehicle types
    vehicle_distribution = {}
    for item in traffic_data:
        vehicle_types = item.get("vehicle_counts", {})
        for vehicle_type, count in vehicle_types.items():
            if vehicle_type not in ['total', 'emergency_vehicles']:
                vehicle_distribution[vehicle_type] = vehicle_distribution.get(vehicle_type, 0) + count
    
    # Timeline data (group by hour)
    timeline_data = []
    hourly_groups: Dict[str, Dict[str, int]] = {}
    
    for item in traffic_data:
        timestamp = item.get("timestamp")
        if timestamp:
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            if hour_key not in hourly_groups:
                hourly_groups[hour_key] = {}
            
            vehicle_types = item.get("vehicle_counts", {})
            for vehicle_type, count in vehicle_types.items():
                if vehicle_type not in ['total', 'emergency_vehicles']:
                    hourly_groups[hour_key][vehicle_type] = hourly_groups[hour_key].get(vehicle_type, 0) + count
    
    for hour_key in sorted(hourly_groups.keys()):
        timeline_data.append({
            "timestamp": hour_key,
            **hourly_groups[hour_key],
            "total": sum(hourly_groups[hour_key].values())
        })
    
    # Peak hours analysis (group by hour of day)
    hour_stats: Dict[int, List[int]] = {}
    for item in traffic_data:
        timestamp = item.get("timestamp")
        if timestamp:
            hour = timestamp.hour
            vehicles = item.get("vehicle_count", 0)
            if hour not in hour_stats:
                hour_stats[hour] = []
            hour_stats[hour].append(vehicles)
    
    peak_hours = []
    for hour, counts in sorted(hour_stats.items()):
        avg_count = sum(counts) / len(counts) if counts else 0
        peak_hours.append({
            "hour": hour,
            "avg_vehicles": round(avg_count, 2),
            "data_points": len(counts)
        })
    
    # Location statistics
    location_stats: Dict[str, Dict[str, Any]] = {}
    for item in traffic_data:
        location = item.get("location_id", "unknown")
        vehicles = item.get("vehicle_count", 0)
        
        if location not in location_stats:
            location_stats[location] = {"total_vehicles": 0, "videos": 0, "emergency": 0}
        
        location_stats[location]["total_vehicles"] += vehicles
        location_stats[location]["videos"] += 1
        location_stats[location]["emergency"] += item.get("emergency_vehicles", 0)
    
    location_list = [
        {"location_id": loc, **stats}
        for loc, stats in location_stats.items()
    ]
    
    return {
        "summary": {
            "total_vehicles": total_vehicles,
            "total_videos": total_videos,
            "avg_vehicles_per_video": round(total_vehicles / total_videos, 2) if total_videos > 0 else 0,
            "emergency_detections": emergency_count
        },
        "vehicle_distribution": vehicle_distribution,
        "timeline_data": timeline_data,
        "peak_hours": sorted(peak_hours, key=lambda x: x["avg_vehicles"], reverse=True),
        "location_stats": location_list
    }


@router.get("/export/csv")
async def export_analytics_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Export analytics data as CSV"""
    collection = await get_traffic_collection()
    
    # Parse dates
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    else:
        start = datetime.utcnow() - timedelta(days=7)
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        end = datetime.utcnow()
    
    query = {"timestamp": {"$gte": start, "$lte": end}}
    
    cursor = collection.find(query).sort("timestamp", 1)
    traffic_data = await cursor.to_list(length=10000)
    
    if not traffic_data:
        raise HTTPException(status_code=404, detail="No data found for the specified date range")
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Timestamp", "Location ID", "Total Vehicles", "Cars", "Motorcycles", 
        "Trucks", "Buses", "Bicycles", "Emergency Vehicles", "Congestion Level", "Average Congestion"
    ])
    
    # Write data rows
    for item in traffic_data:
        timestamp = item.get("timestamp", "")
        location = item.get("location_id", "")
        vehicle_types = item.get("vehicle_counts", {})
        
        writer.writerow([
            timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            location,
            item.get("vehicle_count", 0),
            vehicle_types.get("car", 0),
            vehicle_types.get("motorcycle", 0),
            vehicle_types.get("truck", 0),
            vehicle_types.get("bus", 0),
            vehicle_types.get("bicycle", 0),
            item.get("emergency_vehicles", 0),
            item.get("congestion_level", 0),
            item.get("average_congestion", 0)
        ])
    
    # Prepare response
    output.seek(0)
    filename = f"traffic_analytics_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/last-video")
async def get_last_video_analytics():
    """Get analytics for the most recently processed video"""
    from ..database import Database
    db = Database.get_database()
    jobs_collection = db.video_processing_jobs
    traffic_collection = db.traffic_data
    
    # Get the most recent video job
    cursor = jobs_collection.find().sort("processed_at", -1).limit(1)
    jobs = await cursor.to_list(length=1)
    
    if not jobs:
        raise HTTPException(status_code=404, detail="No videos processed yet")
    
    job = jobs[0]
    job_id = job.get("job_id")
    
    # Get corresponding traffic data
    traffic_data = await traffic_collection.find_one({"job_id": job_id})
    
    if not traffic_data:
        raise HTTPException(status_code=404, detail="Traffic data not found for last video")
    
    return {
        "job_id": job_id,
        "location_id": job.get("location_id"),
        "processed_at": job.get("processed_at"),
        "video_path": job.get("video_path"),
        "output_video": job.get("output_video"),
        "vehicle_count": traffic_data.get("vehicle_count", 0),
        "vehicle_counts": traffic_data.get("vehicle_counts", {}),
        "congestion_level": traffic_data.get("congestion_level", 0),
        "average_congestion": traffic_data.get("average_congestion", 0),
        "emergency_vehicles": traffic_data.get("emergency_vehicles", 0),
        "frames": job.get("frames", {}),
        "timestamp": traffic_data.get("timestamp")
    }


@router.get("/locations")
async def get_all_locations():
    """Get list of all unique locations with video count"""
    collection = await get_traffic_collection()
    
    pipeline = [
        {
            "$group": {
                "_id": "$location_id",
                "total_videos": {"$sum": 1},
                "total_vehicles": {"$sum": "$vehicle_count"},
                "avg_congestion": {"$avg": "$congestion_level"},
                "last_updated": {"$max": "$timestamp"}
            }
        },
        {"$sort": {"last_updated": -1}}
    ]
    
    cursor = collection.aggregate(pipeline)
    locations = await cursor.to_list(length=100)
    
    return [
        {
            "location_id": loc["_id"],
            "total_videos": loc["total_videos"],
            "total_vehicles": loc["total_vehicles"],
            "avg_congestion": round(loc["avg_congestion"], 2),
            "last_updated": loc["last_updated"]
        }
        for loc in locations
    ]


@router.get("/location/{location_id}")
async def get_location_analytics(
    location_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get analytics for a specific location"""
    collection = await get_traffic_collection()
    
    # Parse dates
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    else:
        start = datetime.utcnow() - timedelta(days=7)
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        end = datetime.utcnow()
    
    query = {
        "location_id": location_id,
        "timestamp": {"$gte": start, "$lte": end}
    }
    
    cursor = collection.find(query).sort("timestamp", 1)
    traffic_data = await cursor.to_list(length=1000)
    
    if not traffic_data:
        raise HTTPException(status_code=404, detail=f"No data found for location: {location_id}")
    
    # Calculate statistics
    total_vehicles = sum(item.get("vehicle_count", 0) for item in traffic_data)
    total_videos = len(traffic_data)
    avg_congestion = sum(item.get("congestion_level", 0) for item in traffic_data) / total_videos if total_videos > 0 else 0
    peak_congestion = max(item.get("congestion_level", 0) for item in traffic_data) if traffic_data else 0
    emergency_count = sum(item.get("emergency_vehicles", 0) for item in traffic_data)
    
    # Aggregate vehicle types
    vehicle_distribution = {}
    for item in traffic_data:
        vehicle_types = item.get("vehicle_counts", {})
        for vehicle_type, count in vehicle_types.items():
            if vehicle_type not in ['total', 'emergency_vehicles']:
                vehicle_distribution[vehicle_type] = vehicle_distribution.get(vehicle_type, 0) + count
    
    # Timeline data (group by hour for cleaner visualization)
    hourly_groups: Dict[str, Dict[str, int]] = {}
    for item in traffic_data:
        timestamp = item.get("timestamp")
        if timestamp:
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            if hour_key not in hourly_groups:
                hourly_groups[hour_key] = {}
            
            vehicle_types = item.get("vehicle_counts", {})
            for vehicle_type, count in vehicle_types.items():
                if vehicle_type not in ['total', 'emergency_vehicles']:
                    hourly_groups[hour_key][vehicle_type] = hourly_groups[hour_key].get(vehicle_type, 0) + count
    
    timeline_data = []
    for hour_key in sorted(hourly_groups.keys()):
        timeline_data.append({
            "timestamp": hour_key,
            **hourly_groups[hour_key],
            "total": sum(hourly_groups[hour_key].values())
        })
    
    # Peak hours analysis
    hour_stats: Dict[int, List[int]] = {}
    for item in traffic_data:
        timestamp = item.get("timestamp")
        if timestamp:
            hour = timestamp.hour
            vehicles = item.get("vehicle_count", 0)
            if hour not in hour_stats:
                hour_stats[hour] = []
            hour_stats[hour].append(vehicles)
    
    peak_hours = []
    for hour, counts in sorted(hour_stats.items()):
        avg_count = sum(counts) / len(counts) if counts else 0
        peak_hours.append({
            "hour": hour,
            "avg_vehicles": round(avg_count, 2),
            "data_points": len(counts)
        })
    
    # Location statistics (single location)
    location_stats = [{
        "location_id": location_id,
        "total_vehicles": total_vehicles,
        "videos": total_videos,
        "emergency": emergency_count
    }]
    
    return {
        "location_id": location_id,
        "summary": {
            "total_vehicles": total_vehicles,
            "total_videos": total_videos,
            "avg_vehicles_per_video": round(total_vehicles / total_videos, 2) if total_videos > 0 else 0,
            "avg_congestion": round(avg_congestion, 2),
            "peak_congestion": round(peak_congestion, 2),
            "emergency_detections": emergency_count
        },
        "vehicle_distribution": vehicle_distribution,
        "timeline_data": timeline_data,
        "peak_hours": sorted(peak_hours, key=lambda x: x["avg_vehicles"], reverse=True),
        "location_stats": location_stats,
        "period": {
            "start": start,
            "end": end
        }
    }


@router.delete("/clear-history")
async def clear_analytics_history(
    location_id: Optional[str] = Query(None, description="Clear specific location or all if not provided"),
    confirm: bool = Query(False, description="Must be true to confirm deletion")
):
    """Clear analytics history (admin function)"""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must confirm deletion by setting confirm=true"
        )
    
    from ..database import Database
    db = Database.get_database()
    traffic_collection = db.traffic_data
    jobs_collection = db.video_processing_jobs
    
    query = {"location_id": location_id} if location_id else {}
    
    # Delete traffic data
    traffic_result = await traffic_collection.delete_many(query)
    jobs_result = await jobs_collection.delete_many(query)
    
    return {
        "success": True,
        "deleted_traffic_records": traffic_result.deleted_count,
        "deleted_job_records": jobs_result.deleted_count,
        "location": location_id if location_id else "all locations",
        "message": f"Successfully cleared {traffic_result.deleted_count} traffic records and {jobs_result.deleted_count} job records"
    }
