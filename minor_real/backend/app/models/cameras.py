"""
Camera models for live video stream management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Camera(BaseModel):
    """Camera source configuration"""
    camera_id: str = Field(..., description="Unique camera identifier")
    name: str = Field(..., description="Human-readable camera name")
    rtsp_url: str = Field(..., description="RTSP or HTTP stream URL")
    location_id: str = Field(..., description="Physical location identifier")
    location_name: str = Field(..., description="Human-readable location name")
    direction: Optional[str] = Field(None, description="Traffic direction (e.g., 'North-South', 'East-West')")
    status: str = Field(default="inactive", description="Camera status: active, inactive, error")
    is_streaming: bool = Field(default=False, description="Whether stream is currently active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "camera_id": "cam_001",
                "name": "Main Intersection - North",
                "rtsp_url": "rtsp://192.168.1.100:554/stream",
                "location_id": "loc_001",
                "location_name": "MG Road Junction",
                "direction": "North-South",
                "status": "active"
            }
        }


class CameraCreate(BaseModel):
    """Create new camera"""
    camera_id: str
    name: str
    rtsp_url: str
    location_id: str
    location_name: str
    direction: Optional[str] = None


class CameraUpdate(BaseModel):
    """Update camera configuration"""
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None


class StreamControl(BaseModel):
    """Control stream start/stop"""
    camera_id: str
    action: str = Field(..., description="Action: start or stop")


class LiveDetectionData(BaseModel):
    """Real-time detection data from stream"""
    stream_id: str
    camera_id: str
    location_id: str
    timestamp: str
    vehicle_counts: dict
    emergency_vehicles: list
    congestion_level: str
    average_speed: float
    frame_id: int
