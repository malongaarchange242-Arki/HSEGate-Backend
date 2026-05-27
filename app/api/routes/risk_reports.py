"""Risk Report routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.risk_report import RiskReportCreate, RiskReportUpdate, RiskReportResponse
from app.models.risk_report import RiskReport
from app.models.worker import Worker
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[RiskReportResponse])
async def list_risk_reports(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    severity: str = None,
    zone: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all risk reports with optional filtering.
    
    - **skip**: Number of reports to skip
    - **limit**: Maximum number of reports to return
    - **status_filter**: Filter by status (open, in_progress, resolved, closed)
    - **severity**: Filter by severity (low, medium, high, critical)
    - **zone**: Filter by zone
    
    Requires authentication.
    """
    query = db.query(RiskReport)

    if status_filter:
        query = query.filter(RiskReport.status == status_filter)

    if severity:
        query = query.filter(RiskReport.severity == severity)

    if zone:
        query = query.filter(RiskReport.zone == zone)

    reports = query.order_by(RiskReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.post("", response_model=RiskReportResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_report(
    report: RiskReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new risk report.
    
    - **worker_id**: ID of the worker reporting the risk
    - **title**: Title of the risk report
    - **description**: Detailed description
    - **zone**: Zone where risk was detected
    - **severity**: Severity level
    - **image_url**: Optional risk image URL
    
    Requires authentication.
    """
    # Verify worker exists
    worker = db.query(Worker).filter(Worker.id == report.worker_id).first()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )

    db_report = RiskReport(**report.dict(), status="open")
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return db_report


@router.get("/{report_id}", response_model=RiskReportResponse)
async def get_risk_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific risk report by ID.
    
    Requires authentication.
    """
    db_report = db.query(RiskReport).filter(RiskReport.id == report_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk report not found",
        )

    return db_report


@router.put("/{report_id}", response_model=RiskReportResponse)
async def update_risk_report(
    report_id: int,
    report_update: RiskReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a risk report.
    
    Requires authentication.
    """
    db_report = db.query(RiskReport).filter(RiskReport.id == report_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk report not found",
        )

    update_data = report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a risk report.
    
    Requires authentication.
    """
    db_report = db.query(RiskReport).filter(RiskReport.id == report_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk report not found",
        )

    db.delete(db_report)
    db.commit()

    return None


@router.patch("/{report_id}/status", response_model=RiskReportResponse)
async def update_risk_report_status(
    report_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of a risk report.
    
    - **new_status**: New status (open, in_progress, resolved, closed)
    
    Requires authentication.
    """
    if new_status not in ["open", "in_progress", "resolved", "closed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value",
        )

    db_report = db.query(RiskReport).filter(RiskReport.id == report_id).first()
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk report not found",
        )

    db_report.status = new_status
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return db_report
