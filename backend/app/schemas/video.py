from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VideoResponse(BaseModel):
    id: int
    video_id: str
    channel_id: str
    title: str
    description: str | None = None
    published_at: datetime | None = None
    view_count: int
    like_count: int
    comment_count: int
    trend_score: float
    thumbnail_url: str | None = None

    model_config = {"from_attributes": True}


class TrendingVideoQuery(BaseModel):
    period: str = Field(default="7d", pattern="^(24h|7d|30d)$")
    keyword: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
