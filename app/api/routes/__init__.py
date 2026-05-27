from app.api.routes.auth import router as auth_router
from app.api.routes.workers import router as workers_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.risk_reports import router as risk_reports_router
from app.api.routes.ws import router as ws_router

__all__ = [
    "auth_router",
    "workers_router",
    "incidents_router",
    "risk_reports_router",
    "ws_router",
    # More routers will be added here
    # "detections_router",
    # "reports_router",
    # "alerts_router",
]
