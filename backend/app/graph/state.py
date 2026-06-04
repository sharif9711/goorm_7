from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


def merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = left.copy()
    merged.update(right)
    return merged


class AgentGraphState(TypedDict, total=False):
    """LangGraph shared state for the multi-agent workflow."""

    task_id: str
    query: str
    analysis_type: str
    channel_url: str | None
    competitor_urls: list[str]
    period: str
    user_id: int | None
    project_id: int | None

    status: str
    error: str | None
    current_step: str
    steps_completed: Annotated[list[str], operator.add]

    plan: list[str]
    tool_calls: Annotated[list[dict[str, Any]], operator.add]
    memory_context: list[dict[str, Any]]

    videos: list[dict[str, Any]]
    channels: list[dict[str, Any]]
    channel_analyses: list[dict[str, Any]]
    keywords: list[dict[str, Any]]
    title_patterns: list[dict[str, Any]]
    title_structures: list[dict[str, Any]]
    thumbnail_analysis: dict[str, Any]
    gap_analysis: dict[str, Any]
    user_channel: dict[str, Any] | None
    competitors: list[dict[str, Any]]

    insights: list[str]
    content_ideas: dict[str, list[str]]
    quality_score: float

    requires_human_review: bool
    human_feedback: str | None
    human_approved: bool | None

    report: dict[str, Any]
    evaluation: dict[str, Any]

    created_at: str
