"""Notification service for alerts and messages."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.user import User, UserRole
from app.websocket.manager import manager


class NotificationService:
    """Service for sending notifications and alerts."""

    @staticmethod
    async def create_alert(
        db: Session,
        title: str,
        message: str,
        target_role: str,
    ) -> Alert:
        """
        Create and broadcast an alert.
        
        - **db**: Database session
        - **title**: Alert title
        - **message**: Alert message
        - **target_role**: Target role (admin, hse_supervisor, worker)
        
        Returns created Alert object.
        """
        alert = Alert(
            title=title,
            message=message,
            target_role=target_role,
            status="active",
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Broadcast alert via WebSocket
        await manager.broadcast_alert({
            "alert_id": alert.id,
            "title": title,
            "message": message,
            "target_role": target_role,
            "timestamp": alert.created_at.isoformat(),
        })

        return alert

    @staticmethod
    async def notify_incident(
        db: Session,
        incident_id: int,
        incident_type: str,
        zone: str,
        severity: str,
        worker_id: int,
    ):
        """
        Notify about new incident.
        
        - **db**: Database session
        - **incident_id**: Incident ID
        - **incident_type**: Type of incident
        - **zone**: Zone name
        - **severity**: Severity level
        - **worker_id**: Worker ID
        """
        title = f"Incident: {incident_type.upper()}"
        message = f"Incident in {zone} - {severity.upper()} severity - Worker ID: {worker_id}"

        # Notify HSE supervisors and admins
        await NotificationService.create_alert(
            db=db,
            title=title,
            message=message,
            target_role="hse_supervisor",
        )

        await NotificationService.create_alert(
            db=db,
            title=title,
            message=message,
            target_role="admin",
        )

    @staticmethod
    async def notify_ppe_violation(
        db: Session,
        worker_id: int,
        missing_ppe: List[str],
        zone: str,
    ):
        """
        Notify about PPE violation.
        
        - **db**: Database session
        - **worker_id**: Worker ID
        - **missing_ppe**: List of missing PPE items
        - **zone**: Zone name
        """
        title = "PPE Violation Detected"
        message = f"Missing: {', '.join(missing_ppe).upper()} - Zone: {zone}"

        await NotificationService.create_alert(
            db=db,
            title=title,
            message=message,
            target_role="hse_supervisor",
        )

        await NotificationService.create_alert(
            db=db,
            title=title,
            message=message,
            target_role="admin",
        )

    @staticmethod
    async def clear_alerts(db: Session, alert_ids: List[int]):
        """
        Clear (deactivate) alerts.
        
        - **db**: Database session
        - **alert_ids**: List of alert IDs to clear
        """
        db.query(Alert).filter(Alert.id.in_(alert_ids)).update(
            {Alert.status: "inactive"}
        )
        db.commit()

    @staticmethod
    async def get_active_alerts(
        db: Session,
        target_role: Optional[str] = None,
        limit: int = 100,
    ) -> List[Alert]:
        """
        Get active alerts.
        
        - **db**: Database session
        - **target_role**: Optional role filter
        - **limit**: Maximum number of alerts
        
        Returns list of active alerts.
        """
        query = db.query(Alert).filter(Alert.status == "active")

        if target_role:
            query = query.filter(Alert.target_role == target_role)

        return query.order_by(Alert.created_at.desc()).limit(limit).all()
