from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.services.openai_service import OpenAIService


class ReportAgent(BaseAgent):
    name = "report_agent"

    def __init__(self, openai_service: OpenAIService | None = None):
        self.openai = openai_service or OpenAIService()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        query = context.get("query", "Trend Analysis")
        report_context = {
            "query": query,
            "analysis_type": context.get("analysis_type"),
            "plan": context.get("plan", []),
            "keywords": context.get("keywords", [])[:15],
            "channel_analyses": context.get("channel_analyses", [])[:10],
            "title_patterns": context.get("title_patterns", []),
            "title_structures": context.get("title_structures", []),
            "thumbnail_analysis": context.get("thumbnail_analysis", {}),
            "gap_analysis": context.get("gap_analysis", {}),
            "insights": context.get("insights", []),
            "content_ideas": context.get("content_ideas", {}),
            "quality_score": context.get("quality_score", 0),
            "video_count": len(context.get("videos", [])),
        }

        markdown = await self.openai.generate_report_markdown(report_context)
        summary = context.get("insights", [""])[0] if context.get("insights") else f"{query} 트렌드 분석 완료"

        self.log("Report generated")
        return {
            "report": {
                "title": f"{query} - YouTube 트렌드 리포트",
                "summary": summary[:500],
                "markdown_content": markdown,
            }
        }
