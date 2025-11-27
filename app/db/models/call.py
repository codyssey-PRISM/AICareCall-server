from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.call_message import CallMessage
    from app.db.models.elder import Elder


class Call(Base):
    """통화 기록 테이블"""
    __tablename__ = "calls"
    
    # 기본 정보
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vapi_call_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    
    elder_id: Mapped[int] = mapped_column(Integer, ForeignKey("elders.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # ✨ 추가
    
    # 통화 시간 정보
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 통화 상태 및 결과
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # completed, failed, no_answer, busy
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI가 생성한 요약
    emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True) 
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    messages: Mapped[list["CallMessage"]] = relationship("CallMessage", back_populates="call", cascade="all, delete-orphan")
    elder: Mapped["Elder"] = relationship("Elder", back_populates="calls")