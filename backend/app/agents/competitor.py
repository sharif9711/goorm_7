from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.services.youtube import YouTubeService


class CompetitorAgent(BaseAgent):
    name = "competitor_agent"

    def __init__(self, youtube: YouTubeService | None = None):
        self.youtube = youtube or YouTubeService()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        channel_url = context.get("channel_url")
        competitor_urls = context.get("competitor_urls", [])
        channel_analyses = context.get("channel_analyses", [])

        user_channel = None
        competitors: list[dict[str, Any]] = []

        if channel_url:
            channel_id = self.youtube.extract_channel_id(channel_url)
            if channel_id:
                user_channel = self.youtube.get_channel(channel_id)

        for url in competitor_urls:
            cid = self.youtube.extract_channel_id(url)
            if cid:
                ch = self.youtube.get_channel(cid)
                if ch:
                    competitors.append(ch)

        if not competitors and channel_analyses:
            competitors = [
                {
                    "channel_id": ca["channel_id"],
                    "title": ca["title"],
                    "subscriber_count": ca["subscriber_count"],
                    "view_count": ca["view_count"],
                    "growth_score": ca["growth_score"],
                }
                for ca in channel_analyses[1:6]
            ]

        gap_analysis = self._compute_gap(user_channel, competitors, context)
        self.log(f"Competitor analysis: {len(competitors)} competitors")
        return {
            "user_channel": user_channel,
            "competitors": competitors,
            "gap_analysis": gap_analysis,
        }

    def _compute_gap(
        self,
        user_channel: dict | None,
        competitors: list[dict],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if not user_channel and not competitors:
            return {"opportunities": [], "summary": "비교할 채널이 없습니다."}

        user_subs = user_channel.get("subscriber_count", 0) if user_channel else 0
        user_views = user_channel.get("view_count", 0) if user_channel else 0

        avg_comp_subs = sum(c.get("subscriber_count", 0) for c in competitors) / max(len(competitors), 1)
        avg_comp_views = sum(c.get("view_count", 0) for c in competitors) / max(len(competitors), 1)

        opportunities = []
        if user_subs < avg_comp_subs:
            opportunities.append("구독자 성장: 경쟁 채널 대비 구독자 확보 기회")
        if user_views < avg_comp_views:
            opportunities.append("조회수 개선: 콘텐츠 품질 및 SEO 최적화 필요")

        keywords = context.get("keywords", [])[:5]
        if keywords:
            opportunities.append(f"트렌딩 키워드 활용: {', '.join(k['keyword'] for k in keywords[:3])}")

        title_patterns = context.get("title_patterns", [])[:3]
        if title_patterns:
            opportunities.append(f"제목 패턴 적용: {title_patterns[0]['pattern']}")

        return {
            "user_metrics": {"subscribers": user_subs, "views": user_views},
            "competitor_avg": {"subscribers": round(avg_comp_subs), "views": round(avg_comp_views)},
            "opportunities": opportunities,
            "summary": f"{len(opportunities)}개의 성장 기회 발견",
        }
