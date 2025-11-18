from __future__ import annotations

from functools import lru_cache
from typing import List, Union

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment Variables:
    - DATABASE_URL: SQLAlchemy database URL. Optional when DISABLE_DATABASE=true.
    - DISABLE_DATABASE: "true"/"false" to disable DB usage and start app without a database.
    - CORS_ORIGINS: Comma-separated list of allowed origins, or "*" for all.
    - WS_BASE_PATH: Base path for WebSocket endpoints in docs/help.
    """
    # Database
    DATABASE_URL: Union[str, None] = Field(default=None, description="SQLAlchemy DB URL")
    DISABLE_DATABASE: bool = Field(default=False, description="Disable database usage and start in no-DB mode")

    # CORS
    CORS_ORIGINS: str = Field(default="*", description="Comma-separated origins or '*'")

    # WebSocket
    WS_BASE_PATH: str = Field(default="/ws", description="Base path for WebSocket endpoints")

    def parse_cors_origins(self) -> Union[List[str], str]:
        """
        Parse CORS_ORIGINS env into a list or '*' literal.
        """
        raw = self.CORS_ORIGINS.strip()
        if raw == "*":
            return "*"
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        return parts or ["*"]


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """
    Return a cached instance of Settings loaded from environment variables.
    """
    return _get_cached_settings()


@lru_cache()
def _get_cached_settings() -> Settings:
    """
    Internal cached loader to keep the PUBLIC_INTERFACE cleanly documented above.
    pydantic-settings will auto load .env if present.
    """
    return Settings()
