"""Worker schemas with QR code and face recognition."""

from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class WorkerCreate(BaseModel):
    """Worker creation request with face image."""
    fullname: str = Field(..., min_length=2, max_length=255)
    matricule: Optional[str] = Field(None, min_length=3, max_length=100)  # Auto-generated if not provided
    department: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    face_image_base64: Optional[str] = None  # Face photo in base64
    
    @field_validator('blood_group')
    def validate_blood_group(cls, v):
        if v and v not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            raise ValueError('Invalid blood group')
        return v


class WorkerUpdate(BaseModel):
    """Worker update request."""
    fullname: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    status: Optional[str] = None


class WorkerResponse(BaseModel):
    """Worker response schema."""
    id: int
    worker_uuid: UUID
    fullname: str
    matricule: str
    department: Optional[str]
    position: Optional[str]
    company: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    photo_url: Optional[str]
    badge_id: UUID
    qr_code_url: Optional[str]
    badge_image_url: Optional[str]
    emergency_contact: Optional[str]
    blood_group: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkerQRCodeResponse(BaseModel):
    """QR code generation response."""
    worker_id: int
    worker_uuid: UUID
    fullname: str
    matricule: str
    qr_code_url: str
    badge_image_url: str
    qr_data: str  # Data encoded in QR


class WorkerFaceRegisterResponse(BaseModel):
    """Face registration response."""
    worker_id: int
    face_registered: bool
    face_encoding_stored: bool
    message: str
