"""Main FastAPI application for HSEGate AI Backend."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.connection import engine
from app.database.base import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create all tables (use checkfirst=True to avoid errors)
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("✅ Database tables created/verified")
except Exception as e:
    logger.error(f"❌ Database initialization error: {e}")

# Import routers (with error handling)
try:
    from app.api.routes.auth import router as auth_router
    logger.info("✅ auth_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ auth_router not available: {e}")
    auth_router = None

try:
    from app.api.routes.workers import router as workers_router
    logger.info("✅ workers_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ workers_router not available: {e}")
    workers_router = None

try:
    from app.api.routes.incidents import router as incidents_router
    logger.info("✅ incidents_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ incidents_router not available: {e}")
    incidents_router = None

try:
    from app.api.routes.risk_reports import router as risk_reports_router
    logger.info("✅ risk_reports_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ risk_reports_router not available: {e}")
    risk_reports_router = None

try:
    from app.api.routes.ws import router as ws_router
    logger.info("✅ ws_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ ws_router not available: {e}")
    ws_router = None

try:
    from app.api.routes.ppe import router as ppe_router
    logger.info("✅ ppe_router loaded")
except ImportError as e:
    logger.warning(f"⚠️ ppe_router not available: {e}")
    ppe_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("=" * 50)
    logger.info(f"🚀 HSEGate AI Backend v{settings.APP_VERSION} started")
    logger.info(f"📡 API Docs: http://localhost:8000/docs")
    logger.info(f"🔍 Debug mode: {settings.DEBUG}")
    logger.info("=" * 50)
    yield
    # Shutdown
    logger.info("🛑 HSEGate AI Backend shutdown")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Système intelligent de surveillance HSE par IA",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated QR codes, badges, and face images.
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# Health check endpoints
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "HSEGate AI Backend",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs",
        "api_prefix": "/api/v1",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if engine else "disconnected",
    }


# Include routers (only if they exist)
api_prefix = "/api/v1"

if auth_router:
    app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
if workers_router:
    app.include_router(workers_router, prefix=f"{api_prefix}/workers", tags=["Workers"])
if incidents_router:
    app.include_router(incidents_router, prefix=f"{api_prefix}/incidents", tags=["Incidents"])
if risk_reports_router:
    app.include_router(risk_reports_router, prefix=f"{api_prefix}/risk-reports", tags=["Risk Reports"])
if ws_router:
    app.include_router(ws_router, prefix=f"{api_prefix}/ws", tags=["WebSocket"])
if ppe_router:
    app.include_router(ppe_router, prefix=f"{api_prefix}/ppe", tags=["PPE Detection"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
