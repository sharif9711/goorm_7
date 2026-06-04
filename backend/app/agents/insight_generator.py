from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.services.openai_service import OpenAIService


class InsightGeneratorAgent(BaseAgent):
    name = "insight_generator_agent"

    def __init__(self, openai_service: OpenAIService | None = None):
        self.openai = openai_service or OpenAIService()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        query = context.get("query", "")
        summary_data = {
            "keywords": context.get("keywords", [])[:10],
            "channels": context.get("channel_analyses", [])[:5],
            "title_patterns": context.get("title_patterns", [])[:5],
            "thumbnail_analysis": context.get("thumbnail_analysis", {}),
            "gap_analysis": context.get("gap_analysis", {}),
            "video_count": len(context.get("videos", [])),
        }

        insights = await self.openai.generate_insights(summary_data, query)
        content_ideas: dict[str, list[str]] = {}

        if context.get("analysis_type") in ("content_ideas", "full", "keyword_search"):
            content_ideas = await self.openai.generate_content_ideas(summary_data, query)

        self.log(f"Generated {len(insights)} insights")
        return {"insights": insights, "content_ideas": content_ideas}
