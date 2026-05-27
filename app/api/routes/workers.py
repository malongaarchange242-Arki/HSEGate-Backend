"""Worker routes with QR code and face recognition."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json

from app.schemas.worker import (
    WorkerCreate, WorkerUpdate, WorkerResponse, 
    WorkerQRCodeResponse, WorkerFaceRegisterResponse
)
from app.models.worker import Worker
from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.qrcode_service import qr_service
from app.services.face_service import face_service
from app.services.matricule_service import matricule_service

router = APIRouter()


@router.get("", response_model=List[WorkerResponse])
async def list_workers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all workers."""
    workers = db.query(Worker).all()
    return workers


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def create_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new worker with QR code and face recognition.
    
    - Generates unique UUID for worker
    - Auto-generates matricule if not provided (format: HSE-YYYY-XXXX)
    - Creates QR code for identification
    - Registers face if image provided
    """
    # Generate matricule if not provided
    if not worker.matricule:
        worker.matricule = matricule_service.generate_matricule(db)
    
    # Check if matricule already exists
    existing_worker = db.query(Worker).filter(
        Worker.matricule == worker.matricule
    ).first()
    if existing_worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker with this matricule already exists",
        )
    
    # Check if email already exists
    if worker.email:
        existing_email = db.query(Worker).filter(
            Worker.email == worker.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Create worker
    db_worker = Worker(
        fullname=worker.fullname,
        matricule=worker.matricule,
        department=worker.department,
        position=worker.position,
        company=worker.company,
        phone=worker.phone,
        email=worker.email,
        emergency_contact=worker.emergency_contact,
        blood_group=worker.blood_group,
    )
    
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    
    # Generate QR code and badge
    qr_url, badge_url = qr_service.save_qr_code(
        db_worker.id,
        db_worker.worker_uuid,
        worker.dict()
    )
    db_worker.qr_code_url = qr_url
    db_worker.badge_image_url = badge_url
    
    # Register face if provided
    if worker.face_image_base64:
        encoding, face_url = face_service.register_face(
            db_worker.id, worker.face_image_base64
        )
        if encoding:
            db_worker.face_embedding = json.dumps(encoding)
            db_worker.photo_url = face_url
    
    db.commit()
    db.refresh(db_worker)
    
    return db_worker


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific worker by ID."""
    db_worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )
    return db_worker


@router.get("/by-matricule/{matricule}", response_model=WorkerResponse)
async def get_worker_by_matricule(
    matricule: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a worker by matricule."""
    db_worker = db.query(Worker).filter(Worker.matricule == matricule).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )
    return db_worker


@router.get("/{worker_id}/qrcode", response_model=WorkerQRCodeResponse)
async def get_worker_qrcode(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get worker's QR code."""
    db_worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )
    
    qr_data = {
        "worker_id": db_worker.id,
        "worker_uuid": str(db_worker.worker_uuid),
        "matricule": db_worker.matricule,
        "fullname": db_worker.fullname
    }
    
    return WorkerQRCodeResponse(
        worker_id=db_worker.id,
        worker_uuid=db_worker.worker_uuid,
        fullname=db_worker.fullname,
        matricule=db_worker.matricule,
        qr_code_url=db_worker.qr_code_url or "",
        badge_image_url=db_worker.badge_image_url or "",
        qr_data=json.dumps(qr_data)
    )


@router.post("/{worker_id}/face", response_model=WorkerFaceRegisterResponse)
async def register_worker_face(
    worker_id: int,
    face_image_base64: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register or update worker's face."""
    db_worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )
    
    encoding, face_url = face_service.register_face(worker_id, face_image_base64)
    
    if encoding:
        db_worker.face_embedding = json.dumps(encoding)
        db_worker.photo_url = face_url
        db.commit()
        return WorkerFaceRegisterResponse(
            worker_id=worker_id,
            face_registered=True,
            face_encoding_stored=True,
            message="Face registered successfully"
        )
    else:
        return WorkerFaceRegisterResponse(
            worker_id=worker_id,
            face_registered=False,
            face_encoding_stored=False,
            message="No face detected in image"
        )


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_update: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a worker."""
    db_worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )

    update_data = worker_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_worker, field, value)

    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)

    return db_worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a worker."""
    db_worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found",
        )

    db.delete(db_worker)
    db.commit()
    return None
