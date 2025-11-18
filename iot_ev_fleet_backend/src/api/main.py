from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.database import Base, engine

openapi_tags = [
    {"name": "health", "description": "Service health and diagnostics"},
    {"name": "websocket", "description": "Real-time updates (placeholder)"},
    {"name": "db", "description": "Database utilities (migration/init placeholders)"},
]

app = FastAPI(
    title="IoT EV Fleet Management Backend",
    description="Backend API for ingesting IoT data, handling business logic, and managing the fleet system.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Health Check", description="Returns service health status.")
def health_check():
    """
    Health Check endpoint.

    Returns:
        JSON object indicating the service is healthy.
    """
    return {"message": "Healthy"}


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
    return {"note": "WebSocket endpoints will be documented here once implemented. Expected path: /ws/vehicles"}


@app.get(
    "/db/init",
    tags=["db"],
    summary="Initialize DB schema",
    description="Creates database tables based on current SQLAlchemy models. Use only in development.",
)
def init_db():
    """
    Initialize database tables based on SQLAlchemy models.

    Returns:
        JSON indicating success.
    """
    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Database schema initialized"}
