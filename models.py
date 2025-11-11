"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Time
from sqlalchemy.sql import func
from database import Base


class Callee(Base):
    """
    Model for storing callee (call recipient) information
    """
    __tablename__ = "callees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    custom_info = Column(String, nullable=True)
    
    # Array of weekday preferences (0=Monday, 6=Sunday)
    weekday_preferences = Column(ARRAY(Integer), nullable=False)
    
    # Array of time preferences (stored as strings in HH:MM:SS format)
    time_preferences = Column(ARRAY(String), nullable=False)
    
    # VoIP device token for push notifications
    voip_device_token = Column(String, unique=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Callee(id={self.id}, name='{self.name}', age={self.age})>"

