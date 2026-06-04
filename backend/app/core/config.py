from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import quote_plus, unquote

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _encode_database_url(url: str) -> str:
    """Re-encode credentials so special characters in passwords do not break the URL."""
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "@" not in rest:
        return url
    creds, hostpart = rest.rsplit("@", 1)
    if ":" not in creds:
        return url
    user, password = creds.split(":", 1)
    user = quote_plus(unquote(user), safe="")
    password = quote_plus(unquote(password), safe="")
    return f"{scheme}://{user}:{password}@{hostpart}"


def _normalize_database_url(url: str, async_driver: bool = True) -> str:
    """Convert cloud postgres URLs (Supabase, etc.) to SQLAlchemy format."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if async_driver and url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not async_driver and "+asyncpg" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if "?" in url:
        base, _, query = url.partition("?")
        if "sslmode=" in query:
            url = base
    return _encode_database_url(url)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "YouTube Trend Research Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    PORT: int = 8000

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/youtube_trends"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/youtube_trends"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/callback"

    YOUTUBE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_VISION_MODEL: str = "gpt-4o"

    RATE_LIMIT: str = "100/minute"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    FRONTEND_URL: str = ""

    EMBEDDING_DIMENSION: int = 1536

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        return _normalize_database_url(v, async_driver=True)

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def validate_database_url_sync(cls, v: str) -> str:
        if not v or v == "postgresql://postgres:postgres@localhost:5432/youtube_trends":
            db_url = os.getenv("DATABASE_URL", v)
            return _normalize_database_url(db_url, async_driver=False)
        return _normalize_database_url(v, async_driver=False)

    def get_openai_api_key(self) -> str:
        key = self.OPENAI_API_KEY.strip()
        if key in ("", "your_openai_api_key", "your-key", "sk-xxx"):
            return ""
        return key

    def get_cors_origins(self) -> list[str]:
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.DATABASE_URL_SYNC.startswith("postgresql://postgres:postgres@localhost"):
        settings.DATABASE_URL_SYNC = _normalize_database_url(
            os.getenv("DATABASE_URL", settings.DATABASE_URL_SYNC),
            async_driver=False,
        )
    return settings
