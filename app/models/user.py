"""User model."""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import enum
from app.database.base import Base


class UserRole(str, enum.Enum):
    """User roles."""
    ADMIN = "admin"
    HSE_SUPERVISOR = "hse_supervisor"
    WORKER = "worker"


class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.WORKER.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User {self.email}>"
