"""
Traffic signal models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SignalState(str, Enum):
    """Traffic signal states"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class SignalPhase(BaseModel):
    """Single phase of signal cycle"""
    direction: str = Field(..., description="North/South/East/West")
    state: SignalState
    duration: int = Field(..., ge=0, description="Duration in seconds")


class SignalTiming(BaseModel):
    """Traffic signal timing configuration"""
    signal_id: str = Field(..., description="Traffic signal identifier")
    location_id: str
    phases: List[SignalPhase]
    cycle_length: int = Field(..., ge=30, le=300, description="Total cycle time in seconds")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_adaptive: bool = Field(default=False, description="Whether signal uses adaptive timing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal_id": "signal_01",
                "location_id": "intersection_01",
                "phases": [
                    {"direction": "North-South", "state": "green", "duration": 45},
                    {"direction": "North-South", "state": "yellow", "duration": 5},
                    {"direction": "East-West", "state": "green", "duration": 30},
                    {"direction": "East-West", "state": "yellow", "duration": 5}
                ],
                "cycle_length": 85,
                "is_adaptive": True
            }
        }


class SignalControl(BaseModel):
    """Manual signal control command"""
    signal_id: str
    action: str = Field(..., description="override/reset/adaptive")
    phase_override: Optional[SignalPhase] = None
    reason: Optional[str] = None


class SignalStatus(BaseModel):
    """Current signal status"""
    signal_id: str
    location_id: str
    current_state: SignalState
    current_phase: str
    time_remaining: int = Field(..., ge=0, description="Seconds remaining in current phase")
    is_operational: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)
