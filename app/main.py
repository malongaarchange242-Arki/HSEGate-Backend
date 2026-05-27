"""Main FastAPI application for HSEGate AI Backend."""

import importlib
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
def load_router(module_name: str, router_name: str = "router"):
    try:
        module = importlib.import_module(module_name)
        router = getattr(module, router_name)
        logger.info(f"✅ {module_name} loaded")
        return router
    except Exception as e:
        logger.exception(f"⚠️ Failed to load router {module_name}: {e}")
        return None

auth_router = load_router("app.api.routes.auth")
workers_router = load_router("app.api.routes.workers")
incidents_router = load_router("app.api.routes.incidents")
risk_reports_router = load_router("app.api.routes.risk_reports")
ws_router = load_router("app.api.routes.ws")
ppe_router = load_router("app.api.routes.ppe")

if settings.DEBUG and auth_router is None:
    logger.error("Authentication routes not loaded. /api/v1/auth/* endpoints will be unavailable.")


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

# ==================== CORS MIDDLEWARE (CORRIGÉ) ====================
# Configuration complète pour développement
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
]

# Ajouter les origines du settings si disponibles
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    ALLOWED_ORIGINS.extend(settings.CORS_ORIGINS)

# En développement, ajouter * pour faciliter les tests
if settings.DEBUG:
    ALLOWED_ORIGINS.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logger.info(f"🔥 CORS enabled - Accepting requests from: {ALLOWED_ORIGINS[:5]}...")

# ==================== STATIC FILES ====================
# Serve generated QR codes, badges, and face images.
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"📁 Upload directory: {settings.UPLOAD_DIR.absolute()}")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ==================== EXCEPTION HANDLERS ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# ==================== HEALTH CHECK ENDPOINTS ====================
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


# ==================== INCLUDE ROUTERS ====================
api_prefix = "/api/v1"

if auth_router:
    app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    logger.info("🔐 Auth router registered")
if workers_router:
    app.include_router(workers_router, prefix=f"{api_prefix}/workers", tags=["Workers"])
    logger.info("👥 Workers router registered")
if incidents_router:
    app.include_router(incidents_router, prefix=f"{api_prefix}/incidents", tags=["Incidents"])
    logger.info("⚠️ Incidents router registered")
if risk_reports_router:
    app.include_router(risk_reports_router, prefix=f"{api_prefix}/risk-reports", tags=["Risk Reports"])
    logger.info("📋 Risk reports router registered")
if ws_router:
    app.include_router(ws_router, prefix=f"{api_prefix}/ws", tags=["WebSocket"])
    logger.info("🔌 WebSocket router registered")
if ppe_router:
    app.include_router(ppe_router, prefix=f"{api_prefix}/ppe", tags=["PPE Detection"])
    logger.info("🛡️ PPE Detection router registered")

# Log registered API routes for debugging deployment issues
api_routes = [route.path for route in app.routes if route.path.startswith(api_prefix)]
logger.info(f"📋 Registered API routes ({len(api_routes)}): {api_routes}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )