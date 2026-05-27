"""Alert model."""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
import enum
from app.database.base import Base


class AlertStatus(str, enum.Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertRole(str, enum.Enum):
    """Alert target roles."""
    ADMIN = "admin"
    HSE_SUPERVISOR = "hse_supervisor"
    WORKER = "worker"
    ALL = "all"


class Alert(Base):
    """Alert database model."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    target_role = Column(Enum(AlertRole), default=AlertRole.ALL, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Alert {self.id} - {self.status}>"
