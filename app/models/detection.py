"""Detection model."""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from app.database.base import Base


class Detection(Base):
    """Detection database model from AI service."""
    
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    class_name = Column(String(100), nullable=False)  # helmet, vest, glasses, etc.
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    camera_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Detection {self.class_name} - {self.confidence:.2f}>"
