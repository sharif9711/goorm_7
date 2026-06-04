from __future__ import annotations

from pydantic import BaseModel, Field


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    frequency: int
    growth_rate: float
    competition_score: float
    trend_score: float

    model_config = {"from_attributes": True}


class KeywordAnalysisRequest(BaseModel):
    keyword: str
    limit: int = Field(default=50, ge=1, le=200)
