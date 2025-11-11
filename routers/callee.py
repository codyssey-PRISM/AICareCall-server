from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Callee
from schemas import RegisterCalleeRequest, CalleeResponse

router = APIRouter(prefix="/callee", tags=["Callee Management"])

# TODO: Add carer info to the request


@router.post("/register", response_model=CalleeResponse, status_code=status.HTTP_201_CREATED)
async def register_callee(
    request: RegisterCalleeRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new callee with their preferences and VoIP device token.
    
    - **name**: Callee's name
    - **age**: Callee's age
    - **gender**: Callee's gender
    - **custom_info**: Additional information about the callee
    - **weekday_preferences**: List of preferred weekdays (0=Monday, 6=Sunday)
    - **time_preferences**: List of preferred call times
    - **voip_device_token**: VoIP push notification device token from iOS
    """
    
    # Check if device token already exists
    existing_callee = db.query(Callee).filter(
        Callee.voip_device_token == request.voip_device_token
    ).first()
    
    if existing_callee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device token already registered for callee: {existing_callee.name}"
        )
    
    # Convert time objects to ISO format strings for storage
    time_preferences_str = [t.isoformat() for t in request.time_preferences]
    
    # Create new callee
    new_callee = Callee(
        name=request.name,
        age=request.age,
        gender=request.gender,
        custom_info=request.custom_info,
        weekday_preferences=request.weekday_preferences,
        time_preferences=time_preferences_str,
        voip_device_token=request.voip_device_token
    )
    
    # Add to database
    db.add(new_callee)
    db.commit()
    db.refresh(new_callee)
    
    return new_callee


@router.put("/update/{callee_id}", response_model=CalleeResponse)
async def update_callee(
    callee_id: int,
    request: RegisterCalleeRequest,
    db: Session = Depends(get_db)
):
    """
    Update callee information
    """
    callee = db.query(Callee).filter(Callee.id == callee_id).first()
    
    if not callee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Callee with id {callee_id} not found"
        )
    
    # Check if updating to a token that already exists (and it's not the same callee)
    if request.voip_device_token != callee.voip_device_token:
        existing_callee = db.query(Callee).filter(
            Callee.voip_device_token == request.voip_device_token
        ).first()
        
        if existing_callee:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device token already in use by another callee"
            )
    
    # Convert time objects to ISO format strings
    time_preferences_str = [t.isoformat() for t in request.time_preferences]
    
    # Update fields
    callee.name = request.name
    callee.age = request.age
    callee.gender = request.gender
    callee.custom_info = request.custom_info
    callee.weekday_preferences = request.weekday_preferences
    callee.time_preferences = time_preferences_str
    callee.voip_device_token = request.voip_device_token
    
    db.commit()
    db.refresh(callee)
    
    return callee


@router.delete("/delete/{callee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_callee(
    callee_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a callee
    """
    callee = db.query(Callee).filter(Callee.id == callee_id).first()
    
    if not callee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Callee with id {callee_id} not found"
        )
    
    db.delete(callee)
    db.commit()
    
    return None
