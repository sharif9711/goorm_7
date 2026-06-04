from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent


class ChannelIntelligenceAgent(BaseAgent):
    name = "channel_intelligence_agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        channels = context.get("channels", [])
        videos = context.get("videos", [])
        channel_analyses: list[dict[str, Any]] = []

        videos_by_channel: dict[str, list[dict]] = {}
        for video in videos:
            cid = video.get("channel_id", "")
            videos_by_channel.setdefault(cid, []).append(video)

        for channel in channels:
            cid = channel.get("channel_id", "")
            ch_videos = videos_by_channel.get(cid, [])
            avg_views = sum(v.get("view_count", 0) for v in ch_videos) / max(len(ch_videos), 1)
            upload_frequency = len(ch_videos)

            growth_velocity = 0.0
            if ch_videos:
                recent_views = [v.get("view_count", 0) for v in ch_videos[:5]]
                older_views = [v.get("view_count", 0) for v in ch_videos[5:10]]
                if older_views:
                    growth_velocity = (sum(recent_views) / len(recent_views)) / (
                        sum(older_views) / len(older_views) + 1
                    )

            subs = channel.get("subscriber_count", 1)
            views = channel.get("view_count", 0)
            growth_score = min(100, (avg_views / max(subs, 1)) * 10 + growth_velocity * 20)

            analysis = {
                "channel_id": cid,
                "title": channel.get("title", ""),
                "subscriber_count": channel.get("subscriber_count", 0),
                "video_count": channel.get("video_count", 0),
                "view_count": channel.get("view_count", 0),
                "growth_score": round(growth_score, 2),
                "upload_frequency": upload_frequency,
                "avg_views": round(avg_views, 2),
                "growth_velocity": round(growth_velocity, 2),
            }
            channel_analyses.append(analysis)
            channel["growth_score"] = analysis["growth_score"]

        channel_analyses.sort(key=lambda x: x["growth_score"], reverse=True)
        self.log(f"Analyzed {len(channel_analyses)} channels")
        return {"channel_analyses": channel_analyses}
