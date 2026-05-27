"""Detection service for processing AI detections."""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.detection import Detection
from app.models.incident import Incident
from app.models.worker import Worker
from app.websocket.manager import manager


class DetectionService:
    """Service for handling AI detections and creating incidents."""

    @staticmethod
    async def process_detection(
        db: Session,
        worker_id: Optional[int],
        class_name: str,
        confidence: float,
        camera_id: Optional[str] = None,
    ) -> Detection:
        """
        Process a detection and save to database.
        
        - **db**: Database session
        - **worker_id**: Worker ID (optional)
        - **class_name**: Detected class (e.g., "helmet", "vest")
        - **confidence**: Detection confidence score
        - **camera_id**: Camera ID (optional)
        
        Returns saved Detection object.
        """
        detection = Detection(
            worker_id=worker_id,
            class_name=class_name,
            confidence=confidence,
            camera_id=camera_id,
        )

        db.add(detection)
        db.commit()
        db.refresh(detection)

        # Broadcast detection via WebSocket
        await manager.broadcast_detection({
            "detection_id": detection.id,
            "worker_id": worker_id,
            "class_name": class_name,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp": detection.created_at.isoformat(),
        })

        return detection

    @staticmethod
    async def create_incident_from_detection(
        db: Session,
        worker_id: int,
        incident_type: str,
        description: str,
        zone: str,
        severity: str = "medium",
        image_url: Optional[str] = None,
    ) -> Incident:
        """
        Create an incident from a detection.
        
        - **db**: Database session
        - **worker_id**: Worker ID
        - **incident_type**: Type of incident
        - **description**: Incident description
        - **zone**: Zone where incident occurred
        - **severity**: Severity level
        - **image_url**: Optional image URL
        
        Returns created Incident object.
        """
        incident = Incident(
            worker_id=worker_id,
            incident_type=incident_type,
            description=description,
            zone=zone,
            severity=severity,
            image_url=image_url,
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        # Broadcast incident via WebSocket
        await manager.broadcast_incident({
            "incident_id": incident.id,
            "worker_id": worker_id,
            "incident_type": incident_type,
            "zone": zone,
            "severity": severity,
            "timestamp": incident.created_at.isoformat(),
        })

        return incident

    @staticmethod
    async def check_ppe_compliance(
        db: Session,
        worker_id: int,
        detections: List[Dict],
        zone: str = "unknown",
        camera_id: Optional[str] = None,
    ) -> Dict:
        """
        Check PPE compliance and create incident if needed.
        
        - **db**: Database session
        - **worker_id**: Worker ID
        - **detections**: List of detected items
        - **zone**: Zone name
        - **camera_id**: Camera ID
        
        Returns compliance status.
        """
        detected_items = {d["class_name"].lower() for d in detections}

        # Check for required PPE
        has_helmet = "helmet" in detected_items
        has_vest = "vest" in detected_items

        compliant = has_helmet and has_vest

        # Create incident if non-compliant
        if not compliant:
            missing_ppe = []
            if not has_helmet:
                missing_ppe.append("helmet")
            if not has_vest:
                missing_ppe.append("vest")

            description = f"Missing PPE: {', '.join(missing_ppe)}"

            await DetectionService.create_incident_from_detection(
                db=db,
                worker_id=worker_id,
                incident_type="ppe_violation",
                description=description,
                zone=zone,
                severity="high",
            )

        return {
            "worker_id": worker_id,
            "compliant": compliant,
            "has_helmet": has_helmet,
            "has_vest": has_vest,
            "detected_items": list(detected_items),
        }
