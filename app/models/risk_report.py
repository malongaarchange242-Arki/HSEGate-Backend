"""Risk Report model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from datetime import datetime
import enum
from app.database.base import Base


class ReportStatus(str, enum.Enum):
    """Report status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SeverityLevel(str, enum.Enum):
    """Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskReport(Base):
    """Risk Report database model."""
    
    __tablename__ = "risk_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    zone = Column(String(100), nullable=False)
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM, nullable=False)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RiskReport {self.id} - {self.status}>"
