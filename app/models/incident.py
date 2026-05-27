"""Incident model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime
import enum
from app.database.base import Base


class IncidentType(str, enum.Enum):
    """Incident types."""
    MISSING_HELMET = "missing_helmet"
    MISSING_VEST = "missing_vest"
    MISSING_GLASSES = "missing_glasses"
    UNSAFE_BEHAVIOR = "unsafe_behavior"
    OTHER = "other"


class SeverityLevel(str, enum.Enum):
    """Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base):
    """Incident database model."""
    
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    incident_type = Column(Enum(IncidentType), nullable=False)
    description = Column(String(500), nullable=True)
    zone = Column(String(100), nullable=False)
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM, nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Incident {self.id} - {self.incident_type}>"
