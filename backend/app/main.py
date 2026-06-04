from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from app.api.routes import analysis, auth, channels, keywords, reports, videos
from app.core.config import get_settings
from app.core.database import engine

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.API_PREFIX
app.include_router(auth.router, prefix=api_prefix)
app.include_router(analysis.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(channels.router, prefix=api_prefix)
app.include_router(videos.router, prefix=api_prefix)
app.include_router(keywords.router, prefix=api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
