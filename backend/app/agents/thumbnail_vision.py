from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.services.openai_service import OpenAIService


class ThumbnailVisionAgent(BaseAgent):
    name = "thumbnail_vision_agent"

    def __init__(self, openai_service: OpenAIService | None = None):
        self.openai = openai_service or OpenAIService()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        videos = context.get("videos", [])
        thumbnail_urls = [
            v["thumbnail_url"] for v in videos if v.get("thumbnail_url")
        ][:10]

        if not thumbnail_urls:
            return {"thumbnail_analysis": {"summary": "분석할 썸네일이 없습니다.", "styles": []}}

        analysis = await self.openai.analyze_thumbnails(thumbnail_urls)
        self.log(f"Analyzed {len(thumbnail_urls)} thumbnails")
        return {"thumbnail_analysis": analysis, "thumbnail_urls_analyzed": len(thumbnail_urls)}
