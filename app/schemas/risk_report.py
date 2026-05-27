"""Risk report schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class RiskReportCreate(BaseModel):
    """Risk report creation request."""
    worker_id: int
    title: str
    description: str
    zone: str
    severity: Literal["low", "medium", "high", "critical"]
    image_url: Optional[str] = None


class RiskReportUpdate(BaseModel):
    """Risk report update request."""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["open", "in_progress", "resolved", "closed"]] = None
    image_url: Optional[str] = None


class RiskReportResponse(BaseModel):
    """Risk report response schema."""
    id: int
    worker_id: int
    title: str
    description: str
    zone: str
    severity: str
    status: str
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
