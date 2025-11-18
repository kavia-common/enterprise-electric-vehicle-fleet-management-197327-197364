"""
Database setup for the FastAPI backend, including SQLAlchemy engine, session, and Base metadata.

This module supports two modes:
1) Normal DB mode (default): uses SQLAlchemy with DATABASE_URL.
2) No-DB mode: when DISABLE_DATABASE=true (or DATABASE_URL is absent), engine/session
   creation is deferred and guarded. Dependencies yield None, and callers should
   handle the absence of a DB (return mock/static data or 501).

Environment:
- DATABASE_URL: SQLAlchemy connection string (e.g., postgresql+psycopg2://user:pass@host:port/dbname)
- DISABLE_DATABASE: Set to "true" to start without a database.

Note:
- Do not hardcode secrets. Ask orchestrator to set variables in the .env file.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from src.core.config import get_settings

# Load environment variables from .env if present (pydantic-settings also supports this)
load_dotenv()


class Base(DeclarativeBase):
    """Base class for declarative models."""
    pass


def _get_database_url() -> Optional[str]:
    """
    Resolve DATABASE_URL using central Settings.

    Returns:
        The database URL if available, otherwise None.
    """
    settings = get_settings()
    return settings.DATABASE_URL


def _db_disabled() -> bool:
    """Return True if DISABLE_DATABASE is enabled in settings."""
    return bool(get_settings().DISABLE_DATABASE)


# Lazily-created globals (initialized on first use)
_engine = None
_SessionLocal = None


def _ensure_engine_and_session() -> tuple[Optional[object], Optional[sessionmaker]]:
    """
    Create engine and sessionmaker if not already created and if DB is enabled.

    Returns:
        (engine, SessionLocal) - either or both may be None in no-DB mode.
    """
    global _engine, _SessionLocal
    if _engine is not None or _SessionLocal is not None:
        return _engine, _SessionLocal  # type: ignore[return-value]

    if _db_disabled():
        _engine = None
        _SessionLocal = None
        return _engine, _SessionLocal  # type: ignore[return-value]

    db_url = _get_database_url()
    if not db_url:
        # No URL present; operate in no-DB mode implicitly
        _engine = None
        _SessionLocal = None
        return _engine, _SessionLocal  # type: ignore[return-value]

    # Create SQLAlchemy engine and sessionmaker. Pool_pre_ping helps with stale connections.
    eng = create_engine(db_url, pool_pre_ping=True, future=True)
    _engine = eng
    _SessionLocal = sessionmaker(bind=eng, autocommit=False, autoflush=False, expire_on_commit=False, class_=Session)
    return _engine, _SessionLocal  # type: ignore[return-value]


# PUBLIC_INTERFACE
# Expose placeholders that are safe to import; actual objects may be None in no-DB mode.
engine = None  # Will be set when _ensure_engine_and_session is called and DB is enabled.


def _get_session_local() -> Optional[sessionmaker]:
    """Internal helper to get sessionmaker if DB is available."""
    _, sess = _ensure_engine_and_session()
    return sess


# PUBLIC_INTERFACE
def get_db() -> Generator[Optional[Session], None, None]:
    """
    FastAPI dependency that yields a database session and ensures cleanup.

    In no-DB mode, yields None. Callers must handle None by returning static data,
    disabled responses, or raising HTTPException(status_code=501).
    """
    sess_maker = _get_session_local()
    if not sess_maker:
        # No DB available
        yield None
        return

    db = sess_maker()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Optional[Session], None, None]:
    """
    Context manager for DB sessions for non-FastAPI contexts (e.g., scripts).

    In no-DB mode, yields None.

    Example:
        with db_session() as session:
            if session is None:
                # handle no-DB behavior
                ...
            else:
                # use session normally
                ...
    """
    sess_maker = _get_session_local()
    if not sess_maker:
        yield None
        return

    session = sess_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
