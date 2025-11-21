from pydantic import BaseModel
from datetime import datetime, time

class ElderCreate(BaseModel):
    name: str
    relationship: str
    phone: str
    residence: str
    health_condition: str
    begin_date: datetime
    end_date: datetime | None = None
    ask_meal: bool = True
    ask_medication: bool = True
    ask_emotion: bool = True
    ask_special_event: bool = True
    additional_info: str | None = None
    call_weekdays: list[str]
    call_times: list[time]


class ElderResponse(BaseModel):
    id: int
    user_id: int
    name: str
    relationship: str
    phone: str
    residence_type: str
    health_condition: str
    begin_date: datetime
    end_date: datetime | None
    ask_meal: bool
    ask_medication: bool
    ask_emotion: bool
    ask_special_event: bool
    additional_info: str | None
    
    class Config:
        from_attributes = True