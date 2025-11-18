"""
Database setup for the FastAPI backend, including SQLAlchemy engine, session, and Base metadata.

This module loads the DATABASE_URL from environment variables, initializes the SQLAlchemy engine
and sessionmaker, and provides a dependency for FastAPI routes to acquire a database session.

Environment:
- DATABASE_URL: SQLAlchemy connection string (e.g., postgresql+psycopg2://user:pass@host:port/dbname)

Note:
- Do not hardcode secrets. Ask orchestrator to set DATABASE_URL in the .env file.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Load environment variables from .env if present
load_dotenv()


class Base(DeclarativeBase):
    """Base class for declarative models."""
    pass


def _get_database_url() -> str:
    """
    Resolve DATABASE_URL from environment.

    Raises:
        RuntimeError: If DATABASE_URL is not set.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Please set it via environment or .env. "
            "Refer to .env.example for the expected format."
        )
    return db_url


# Create SQLAlchemy engine and sessionmaker
# Pool_pre_ping helps with stale connections.
engine = create_engine(_get_database_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=Session)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for DB sessions for non-FastAPI contexts (e.g., scripts).

    Example:
        with db_session() as session:
            # use session
            ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
