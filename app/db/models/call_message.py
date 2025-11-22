from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.call import Call

class CallMessage(Base):
    """통화 메시지 로그 테이블"""
    __tablename__ = "call_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_id: Mapped[int] = mapped_column(Integer, ForeignKey("calls.id", ondelete="CASCADE"), nullable=False)
    
    # 메시지 정보
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 타이밍
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 실제 발화 시각
    
    # Relationship
    call: Mapped["Call"] = relationship("Call", back_populates="messages")