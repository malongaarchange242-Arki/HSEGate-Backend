"""Access log model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.database.base import Base


class AccessLog(Base):
    """Access log database model."""
    
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    access_status = Column(String(50), nullable=False)  # approved, denied
    missing_ppe = Column(String(255), nullable=True)  # comma-separated list of missing items
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AccessLog {self.worker_id} - {self.access_status}>"
