from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Literal


class RegisterRequest(BaseModel):
    """User registration request."""
    fullname: str
    email: str
    password: str
    role: Literal["admin", "hse_supervisor", "worker"] = "worker"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password length."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class LoginRequest(BaseModel):
    """User login request."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    fullname: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True