"""Elder 모델"""
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Elder(Base):
    """어르신 테이블"""
    __tablename__ = "elders"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    residence_type: Mapped[str] = mapped_column(String(255), nullable=False)
    health_condition: Mapped[str] = mapped_column(String(511), nullable=False)
    begin_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ask_meal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ask_medication: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ask_emotion: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ask_special_event: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    additional_info: Mapped[str] = mapped_column(String(511), nullable=True)
    invite_code: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Elder(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

