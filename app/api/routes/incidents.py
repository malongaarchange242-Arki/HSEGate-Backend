"""Incident routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.models.incident import Incident
from app.models.worker import Worker
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    skip: int = 0,
    limit: int = 100,
    zone: str = None,
    severity: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all incidents with optional filtering.
    
    - **skip**: Number of incidents to skip
    - **limit**: Maximum number of incidents to return
    - **zone**: Filter by zone
    - **severity**: Filter by severity (low, medium, high, critical)
    
    Requires authentication.
    """
    query = db.query(Incident)

    if zone:
        query = query.filter(Incident.zone == zone)

    if severity:
        query = query.filter(Incident.severity == severity)

    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new incident.
    
    - **worker_id**: ID of the worker involved
    - **incident_type**: Type of incident (e.g., "helmet_missing", "no_vest")
    - **description**: Detailed description
    - **zone**: Zone where incident occurred
    - **severity**: Severity level
    - **image_url**: Optional incident image URL
    
    Requires authentication.
    """
    # Verify worker exists
    worker = db.query(Worker).filter(Worker.id == incident.worker_id).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )

    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific incident by ID.
    
    Requires authentication.
    """
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return db_incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an incident.
    
    Requires authentication.
    """
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    update_data = incident_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_incident, field, value)

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an incident.
    
    Requires authentication.
    """
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    db.delete(db_incident)
    db.commit()

    return None


@router.get("/stats/summary", response_model=dict)
async def get_incident_stats(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get incident statistics for the last N days.
    
    - **days**: Number of days to include in stats (default: 7)
    
    Requires authentication.
    """
    date_threshold = datetime.utcnow() - timedelta(days=days)

    total_incidents = db.query(Incident).filter(
        Incident.created_at >= date_threshold
    ).count()

    by_severity = db.query(Incident.severity).filter(
        Incident.created_at >= date_threshold
    ).all()

    severity_count = {
        "low": sum(1 for s in by_severity if s[0] == "low"),
        "medium": sum(1 for s in by_severity if s[0] == "medium"),
        "high": sum(1 for s in by_severity if s[0] == "high"),
        "critical": sum(1 for s in by_severity if s[0] == "critical"),
    }

    return {
        "total": total_incidents,
        "by_severity": severity_count,
        "days": days,
    }
