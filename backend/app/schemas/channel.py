from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChannelResponse(BaseModel):
    id: int
    channel_id: str
    title: str
    description: str | None = None
    subscriber_count: int
    video_count: int
    view_count: int
    growth_score: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChannelAnalysisRequest(BaseModel):
    channel_url: str
    competitor_urls: list[str] = Field(default_factory=list)


class ChannelGrowthAnalysis(BaseModel):
    channel_id: str
    title: str
    growth_score: float
    upload_frequency: float
    avg_views: float
    growth_velocity: float
    subscriber_count: int
    insights: list[str] = Field(default_factory=list)
