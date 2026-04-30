from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    location = Column(String)
    priority = Column(String)
    details = Column(Text)
    status = Column(String, default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())