"""Incident schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class IncidentCreate(BaseModel):
    """Incident creation request."""
    worker_id: int
    incident_type: str
    description: str
    zone: str
    severity: Literal["low", "medium", "high", "critical"]
    image_url: Optional[str] = None


class IncidentUpdate(BaseModel):
    """Incident update request."""
    description: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    image_url: Optional[str] = None


class IncidentResponse(BaseModel):
    """Incident response schema."""
    id: int
    worker_id: int
    incident_type: str
    description: str
    zone: str
    severity: str
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
