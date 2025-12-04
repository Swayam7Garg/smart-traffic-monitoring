"""
Traffic-related data models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class VehicleType(str, Enum):
    """Vehicle classification types"""
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    UNKNOWN = "unknown"


class TrafficData(BaseModel):
    """Real-time traffic data model"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location_id: str = Field(..., description="Intersection or road segment ID")
    vehicle_count: int = Field(..., ge=0, description="Number of vehicles detected")
    vehicle_types: Dict[str, int] = Field(default_factory=dict, description="Count by vehicle type")
    average_speed: Optional[float] = Field(None, ge=0, description="Average speed in km/h")
    congestion_level: int = Field(..., ge=0, le=100, description="Congestion percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00",
                "location_id": "intersection_01",
                "vehicle_count": 25,
                "vehicle_types": {"car": 18, "bus": 2, "truck": 3, "motorcycle": 2},
                "average_speed": 35.5,
                "congestion_level": 65
            }
        }


class VehicleDetection(BaseModel):
    """Individual vehicle detection"""
    vehicle_id: str = Field(..., description="Unique tracking ID")
    vehicle_type: VehicleType
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence score")
    bbox: List[int] = Field(..., description="Bounding box [x, y, width, height]")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location_id: str


class TrafficSummary(BaseModel):
    """Traffic summary statistics"""
    location_id: str
    time_period: str = Field(..., description="hourly/daily/weekly")
    total_vehicles: int
    peak_hour: Optional[str] = None
    average_congestion: float
    vehicle_distribution: Dict[str, int]
