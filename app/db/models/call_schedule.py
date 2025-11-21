"""Elder 모델"""
from datetime import time
from sqlalchemy import String, Integer, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CallSchedule(Base):
    """통화 스케줄 테이블"""
    __tablename__ = "call_schedules"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    elder_id: Mapped[int] = mapped_column(Integer, ForeignKey("elders.id"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(10), nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    
    def __repr__(self) -> str:
        return f"<CallSchedule(id={self.id}, elder_id={self.elder_id}, day_of_week={self.day_of_week}, time={self.time})>"

