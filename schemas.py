"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import time, datetime


class RegisterCalleeRequest(BaseModel):
    """Request model for registering a callee"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., min_length=1, max_length=20)
    custom_info: str = Field(default="")
    weekday_preferences: list[int] = Field(..., min_items=1)  # 0-6 (Mon-Sun)
    time_preferences: list[time] = Field(..., min_items=1)
    voip_device_token: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "age": 75,
                "gender": "male",
                "custom_info": "요통이 있음, 매일 아침 산책",
                "weekday_preferences": [0, 2, 4],  # Monday, Wednesday, Friday
                "time_preferences": ["09:00:00", "14:00:00"],
                "voip_device_token": "693e9a147dfb8ebbb5ed31eff419313d4af80607f63255dd673c61b33be1c1d7"
            }
        }


class CalleeResponse(BaseModel):
    """Response model for callee data"""
    id: int
    name: str
    age: int
    gender: str
    custom_info: str
    weekday_preferences: list[int]
    time_preferences: list[str]  # Time objects serialized as strings
    voip_device_token: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be converted

