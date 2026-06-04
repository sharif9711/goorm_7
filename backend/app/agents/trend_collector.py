from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.services.youtube import YouTubeService


class TrendCollectorAgent(BaseAgent):
    name = "trend_collector_agent"

    def __init__(self, youtube: YouTubeService | None = None):
        self.youtube = youtube or YouTubeService()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        query = context.get("query", "")
        period = context.get("period", "7d")
        channel_url = context.get("channel_url")
        analysis_type = context.get("analysis_type", "keyword_search")

        videos: list[dict[str, Any]] = []
        channels: list[dict[str, Any]] = []

        if analysis_type in ("channel", "competitor") and channel_url:
            channel_id = self.youtube.extract_channel_id(channel_url)
            if channel_id:
                channel = self.youtube.get_channel(channel_id)
                if channel:
                    channels.append(channel)
                    videos.extend(self.youtube.get_channel_videos(channel_id, max_results=50))
        else:
            search_results = self.youtube.search_videos(query, max_results=50, order="viewCount")
            videos.extend(search_results)
            channel_ids = list({v["channel_id"] for v in videos if v.get("channel_id")})
            for cid in channel_ids[:10]:
                ch = self.youtube.get_channel(cid)
                if ch:
                    channels.append(ch)

        if analysis_type == "trending":
            trending = self.youtube.get_trending_videos(region_code="KR", max_results=30)
            videos = trending + videos

        self.log(f"Collected {len(videos)} videos and {len(channels)} channels")
        return {"videos": videos, "channels": channels, "period": period}
