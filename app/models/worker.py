"""Worker model with UUID, badge and face recognition."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database.base import Base


class Worker(Base):
    """Worker database model with enhanced features."""
    
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    fullname = Column(String(255), nullable=False)
    matricule = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    photo_url = Column(Text, nullable=True)
    face_embedding = Column(Text, nullable=True)  # Stored as base64
    badge_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    qr_code_url = Column(Text, nullable=True)
    badge_image_url = Column(Text, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    blood_group = Column(String(20), nullable=True)
    status = Column(String(50), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Worker {self.matricule} - {self.fullname}>"
