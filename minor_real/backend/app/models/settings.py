from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Signal Timing Models
class SignalTiming(BaseModel):
    location_id: str
    location_name: str
    vehicle_type: str
    green_duration: int = Field(ge=10, le=120)
    red_duration: int = Field(ge=10, le=120)
    time_period: Literal['peak', 'normal', 'night']
    updated_at: Optional[datetime] = None

class SignalTimingUpdate(BaseModel):
    green_duration: Optional[int] = Field(None, ge=10, le=120)
    red_duration: Optional[int] = Field(None, ge=10, le=120)

# Location Models
class Location(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    camera_id: str
    status: Literal['active', 'inactive'] = 'active'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    camera_id: str
    status: Literal['active', 'inactive'] = 'active'

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    camera_id: Optional[str] = None
    status: Optional[Literal['active', 'inactive']] = None

# Detection Configuration Models
class DetectionConfig(BaseModel):
    confidence_threshold: float = Field(ge=0.1, le=0.9)
    iou_threshold: float = Field(ge=0.1, le=0.9)
    emergency_color_threshold: int = Field(ge=20, le=80)
    autorickshaw_size_threshold: int = Field(ge=10000, le=50000)
    frame_skip: int = Field(ge=1, le=10)
    updated_at: Optional[datetime] = None

class DetectionConfigUpdate(BaseModel):
    confidence_threshold: Optional[float] = Field(None, ge=0.1, le=0.9)
    iou_threshold: Optional[float] = Field(None, ge=0.1, le=0.9)
    emergency_color_threshold: Optional[int] = Field(None, ge=20, le=80)
    autorickshaw_size_threshold: Optional[int] = Field(None, ge=10000, le=50000)
    frame_skip: Optional[int] = Field(None, ge=1, le=10)

# System Settings Models
class SystemSettings(BaseModel):
    auto_refresh_interval: int = Field(ge=1000, le=30000)  # milliseconds
    max_video_size_mb: int = Field(ge=100, le=2000)
    enable_notifications: bool = True
    dark_mode: bool = False
    language: str = 'en'
    updated_at: Optional[datetime] = None

class SystemSettingsUpdate(BaseModel):
    auto_refresh_interval: Optional[int] = Field(None, ge=1000, le=30000)
    max_video_size_mb: Optional[int] = Field(None, ge=100, le=2000)
    enable_notifications: Optional[bool] = None
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
