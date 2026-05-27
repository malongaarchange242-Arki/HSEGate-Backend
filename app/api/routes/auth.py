"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.models.user import User
from app.database.connection import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.core.config import settings
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **fullname**: User's full name
    - **email**: Unique email address
    - **password**: User password (will be hashed)
    - **role**: User role (admin, hse_supervisor, worker)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    db_user = User(
        fullname=request.fullname,
        email=request.email,
        password_hash=hashed_password,
        role=request.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login and get JWT token.
    
    - **email**: User email
    - **password**: User password
    """
    # Find user by email
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(request.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "role": db_user.role},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
