"""Security utilities for JWT and password handling."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password using bcrypt."""
    # Limit to 72 chars for bcrypt
    truncated = plain_password[:72]
    try:
        return bcrypt.checkpw(
            truncated.encode("utf-8"),
            hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password,
        )
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for a plain password."""
    # Limit to 72 chars for bcrypt
    truncated = password[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(truncated.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
