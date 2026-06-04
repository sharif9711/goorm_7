from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    analysis_type: str = Field(
        default="keyword_search",
        pattern="^(keyword_search|trending|channel|competitor|title|thumbnail|content_ideas|full)$",
    )
    channel_url: str | None = None
    competitor_urls: list[str] = Field(default_factory=list)
    period: str = Field(default="7d", pattern="^(24h|7d|30d)$")
    project_id: int | None = None


class AnalyzeResponse(BaseModel):
    task_id: str
    status: str
    message: str


class AnalysisResult(BaseModel):
    task_id: str
    status: str
    query: str
    analysis_type: str
    plan: list[str] = Field(default_factory=list)
    steps_completed: list[str] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    insights: list[str] = Field(default_factory=list)
    content_ideas: dict[str, list[str]] = Field(default_factory=dict)
    quality_score: float = 0.0
    evaluation: dict[str, Any] = Field(default_factory=dict)
    requires_human_review: bool = False
    report_id: int | None = None
    created_at: datetime | None = None


class HumanReviewRequest(BaseModel):
    approved: bool
    feedback: str | None = None


class WorkflowStatusResponse(BaseModel):
    task_id: str
    status: str
    current_step: str | None = None
    steps_completed: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    quality_score: float = 0.0
    evaluation: dict[str, Any] = Field(default_factory=dict)
    interrupt_payload: dict[str, Any] | None = None


class ReportCreate(BaseModel):
    title: str
    summary: str | None = None
    markdown_content: str
    project_id: int | None = None
    analysis_type: str = "custom"


class ReportResponse(BaseModel):
    id: int
    project_id: int | None = None
    user_id: int
    title: str
    summary: str | None = None
    markdown_content: str | None = None
    analysis_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrendOverview(BaseModel):
    top_keywords: list[dict[str, Any]] = Field(default_factory=list)
    rising_channels: list[dict[str, Any]] = Field(default_factory=list)
    rising_videos: list[dict[str, Any]] = Field(default_factory=list)
    recent_analyses: list[dict[str, Any]] = Field(default_factory=list)
    content_recommendations: list[str] = Field(default_factory=list)
