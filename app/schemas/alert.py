"""Alert schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class AlertCreate(BaseModel):
    """Alert creation request."""
    title: str
    message: str
    target_role: Literal["admin", "hse_supervisor", "worker"]


class AlertUpdate(BaseModel):
    """Alert update request."""
    status: Literal["active", "inactive", "resolved"]


class AlertResponse(BaseModel):
    """Alert response schema."""
    id: int
    title: str
    message: str
    target_role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
