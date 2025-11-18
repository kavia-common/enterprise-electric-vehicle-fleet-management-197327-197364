from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.db.database import Base, _ensure_engine_and_session  # type: ignore
from src.core.config import get_settings

openapi_tags = [
    {"name": "health", "description": "Service health and diagnostics"},
    {"name": "websocket", "description": "Real-time updates (placeholder)"},
    {"name": "db", "description": "Database utilities (migration/init placeholders)"},
]

# Load settings once at startup
settings = get_settings()

app = FastAPI(
    title="IoT EV Fleet Management Backend",
    description="Backend API for ingesting IoT data, handling business logic, and managing the fleet system.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Configure CORS based on settings
cors_origins = settings.parse_cors_origins()
if cors_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = cors_origins  # type: ignore[assignment]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Health Check", description="Returns service health status.")
def health_check():
    """
    Health Check endpoint.

    Returns:
        JSON object indicating the service is healthy and whether DB is disabled.
    """
    return {"message": "Healthy", "db_disabled": bool(settings.DISABLE_DATABASE)}


@app.get(
    "/ws-info",
    tags=["websocket"],
    summary="WebSocket usage",
    description="Placeholder for WebSocket usage. Connect to /ws/vehicles for real-time vehicle updates (to be implemented).",
    operation_id="websocket_usage_info",
)
def websocket_info():
    """
    WebSocket usage help endpoint.

    Returns:
        Instructions for WebSocket connection once the feature is implemented.
    """
    return {
        "note": "WebSocket endpoints will be documented here once implemented.",
        "expected_base_path": settings.WS_BASE_PATH,
        "example_vehicle_path": f"{settings.WS_BASE_PATH}/vehicles",
    }


@app.get(
    "/db/init",
    tags=["db"],
    summary="Initialize DB schema",
    description="Creates database tables based on current SQLAlchemy models. Use only in development. Disabled in no-DB mode.",
)
def init_db():
    """
    Initialize database tables based on SQLAlchemy models.

    Returns:
        JSON indicating success, or 501 when database is disabled or unavailable.
    """
    settings_local = settings  # already loaded at module import
    if settings_local.DISABLE_DATABASE:
        raise HTTPException(status_code=501, detail="Database is disabled (DISABLE_DATABASE=true).")

    engine, _ = _ensure_engine_and_session()  # type: ignore[assignment]
    if engine is None:
        raise HTTPException(status_code=501, detail="No database configured (missing DATABASE_URL).")

    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Database schema initialized"}
