"""Configuration settings for the application."""

import json
import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # ==================== APP ====================
    APP_NAME: str = Field(default="HSEGate AI Backend", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=True, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # ==================== DATABASE ====================
    DATABASE_URL: str = Field(
        default="postgresql://hsegate_user:password@localhost:5432/hsegate_db",
        description="PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections")

    # ==================== SECURITY ====================
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production-please",
        description="JWT secret key"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Token expiry in minutes")

    # ==================== AI / YOLO ====================
    YOLO_MODEL_PATH: str = Field(
        default="yolov8n.pt",
        description="Path or name of YOLO model (e.g. 'yolov8n.pt' to let Ultralytics download)"
    )
    CONFIDENCE_THRESHOLD: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection confidence")
    IOU_THRESHOLD: float = Field(default=0.45, ge=0.0, le=1.0, description="NMS IoU threshold")
    TRACKING_ENABLED: bool = Field(default=True, description="Enable ByteTrack tracking")

    # ==================== REDIS ====================
    REDIS_URL: Optional[str] = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_TTL: int = Field(default=3600, description="Redis cache TTL in seconds")

    # ==================== FILE UPLOADS ====================
    UPLOAD_DIR: Path = Field(default=Path("./uploads"), description="Upload directory")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Max upload size (10MB)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".mp4", ".avi"],
        description="Allowed file extensions"
    )

    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5500",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5500",
        ],
        description="Allowed CORS origins"
    )

    # ==================== WEBSOCKET ====================
    WS_MAX_CONNECTIONS: int = Field(default=100, description="Max WebSocket connections")
    WS_PING_INTERVAL: int = Field(default=20, description="WebSocket ping interval (seconds)")

    # ==================== ALERTS ====================
    ALERT_COOLDOWN_SECONDS: int = Field(default=10, description="Alert cooldown to avoid spam")
    ENABLE_SOUND_ALERTS: bool = Field(default=True, description="Enable sound alerts")
    ENABLE_SMS_ALERTS: bool = Field(default=False, description="Enable SMS alerts")
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, description="Twilio account SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, description="Twilio auth token")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, description="Twilio phone number")

    # ==================== VALIDATORS ====================
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, v) -> bool:
        """Accept common environment labels for debug mode."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            value = v.strip().lower()
            if value in {"1", "true", "yes", "y", "on", "debug", "development", "dev"}:
                return True
            if value in {"0", "false", "no", "n", "off", "release", "production", "prod"}:
                return False
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Allow CORS origins as JSON, comma-separated strings, or lists."""
        if isinstance(v, str):
            value = v.strip()
            if value.startswith("["):
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return v

    @field_validator("UPLOAD_DIR", mode="before")
    @classmethod
    def create_upload_dir(cls, v: Path) -> Path:
        """Create upload directory if it doesn't exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("YOLO_MODEL_PATH")
    @classmethod
    def validate_model_path(cls, v: str) -> str:
        """Validate YOLO model path."""
        if not os.path.exists(v) and v.startswith("./models/"):
            os.makedirs(os.path.dirname(v), exist_ok=True)
            print(f"Warning: Model not found at {v}. Download will be attempted.")
        return v

    # ==================== PROPERTIES ====================
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Create instance
settings = Settings()

# Print config on startup (only in debug)
if settings.DEBUG:
    print("=" * 50)
    print("HSEGate AI Configuration")
    print("=" * 50)
    print(f"APP: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"MODE: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    print(f"DB: {settings.DATABASE_URL.split('@')[0]}@...")
    print(f"REDIS: {settings.REDIS_URL}")
    print(f"YOLO: {settings.YOLO_MODEL_PATH}")
    print(f"UPLOAD: {settings.UPLOAD_DIR}")
    print("=" * 50)
