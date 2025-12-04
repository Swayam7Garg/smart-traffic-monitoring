"""
Violation and alert models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ViolationType(str, Enum):
    """Types of traffic violations"""
    RED_LIGHT = "red_light"
    SPEEDING = "speeding"
    WRONG_WAY = "wrong_way"
    ILLEGAL_PARKING = "illegal_parking"
    LANE_VIOLATION = "lane_violation"
    OTHER = "other"


class Violation(BaseModel):
    """Traffic violation record"""
    violation_id: Optional[str] = None
    violation_type: ViolationType
    location_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vehicle_id: Optional[str] = None
    vehicle_type: Optional[str] = None
    evidence_image: Optional[str] = Field(None, description="Path to evidence image")
    severity: int = Field(..., ge=1, le=5, description="Violation severity level")
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "violation_type": "red_light",
                "location_id": "intersection_01",
                "timestamp": "2024-01-15T10:45:30",
                "vehicle_id": "VH_12345",
                "vehicle_type": "car",
                "severity": 4,
                "description": "Vehicle crossed intersection during red signal"
            }
        }


class AlertType(str, Enum):
    """Alert notification types"""
    CONGESTION = "congestion"
    ACCIDENT = "accident"
    VIOLATION = "violation"
    SIGNAL_MALFUNCTION = "signal_malfunction"
    EMERGENCY_VEHICLE = "emergency_vehicle"
    INFO = "info"


class Alert(BaseModel):
    """System alert/notification"""
    alert_id: Optional[str] = None
    alert_type: AlertType
    location_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: int = Field(..., ge=1, le=5, description="Alert priority level")
    message: str
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_type": "congestion",
                "location_id": "intersection_01",
                "severity": 3,
                "message": "Heavy traffic congestion detected. 45 vehicles waiting.",
                "is_resolved": False
            }
        }
