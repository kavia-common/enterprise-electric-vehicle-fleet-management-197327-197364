"""
Database package initializer exposing common symbols.

In no-DB mode, `engine` may be None and `get_db()` yields None.
Only import and re-export symbols that are safe at import time.
"""
from .database import Base, engine, get_db, db_session  # noqa: F401
