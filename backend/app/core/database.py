from __future__ import annotations

import ssl
from collections.abc import AsyncGenerator

import certifi
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

_connect_args: dict = {}
if "supabase.com" in settings.DATABASE_URL:
    _ssl_context = ssl.create_default_context(cafile=certifi.where())
    if settings.DEBUG:
        # macOS system Python may lack root certs — allow local dev only
        _ssl_context.check_hostname = False
        _ssl_context.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = _ssl_context

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args=_connect_args,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
