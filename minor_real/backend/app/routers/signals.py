"""
Traffic signals API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.signals import SignalTiming, SignalControl, SignalStatus
from ..database import get_signals_collection

router = APIRouter()


@router.get("/", response_model=List[SignalStatus])
async def get_all_signals():
    """Get status of all traffic signals"""
    collection = await get_signals_collection()
    cursor = collection.find({})
    signals = await cursor.to_list(length=100)
    
    return [SignalStatus(**signal) for signal in signals]


@router.get("/{signal_id}", response_model=SignalStatus)
async def get_signal_status(signal_id: str):
    """Get status of a specific traffic signal"""
    collection = await get_signals_collection()
    signal = await collection.find_one({"signal_id": signal_id})
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return SignalStatus(**signal)


@router.post("/timing", response_model=SignalTiming)
async def update_signal_timing(timing: SignalTiming):
    """Update traffic signal timing configuration"""
    collection = await get_signals_collection()
    
    timing_dict = timing.model_dump()
    result = await collection.update_one(
        {"signal_id": timing.signal_id},
        {"$set": timing_dict},
        upsert=True
    )
    
    return timing


@router.post("/control", response_model=dict)
async def control_signal(control: SignalControl):
    """Manually control traffic signal"""
    collection = await get_signals_collection()
    
    signal = await collection.find_one({"signal_id": control.signal_id})
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    # Process control action
    update_data = {"last_control_action": control.action}
    
    if control.action == "override" and control.phase_override:
        update_data["override_phase"] = control.phase_override.model_dump()
    elif control.action == "reset":
        update_data["override_phase"] = None
    
    await collection.update_one(
        {"signal_id": control.signal_id},
        {"$set": update_data}
    )
    
    return {"message": f"Signal {control.signal_id} control action '{control.action}' applied"}


@router.get("/location/{location_id}", response_model=List[SignalStatus])
async def get_signals_by_location(location_id: str):
    """Get all signals for a specific location"""
    collection = await get_signals_collection()
    cursor = collection.find({"location_id": location_id})
    signals = await cursor.to_list(length=50)
    
    if not signals:
        raise HTTPException(status_code=404, detail="No signals found for location")
    
    return [SignalStatus(**signal) for signal in signals]
