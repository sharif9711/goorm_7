from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    name = "critic_agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        insights = context.get("insights", [])
        content_ideas = context.get("content_ideas", {})

        deduped_insights = list(dict.fromkeys(insights))
        validated_insights = [i for i in deduped_insights if len(i) > 10 and not self._is_hallucination(i, context)]

        for category in content_ideas:
            ideas = content_ideas[category]
            content_ideas[category] = list(dict.fromkeys(ideas))[:20]

        quality_score = self._calculate_quality(context, validated_insights)

        self.log(f"Quality score: {quality_score}")
        return {
            "insights": validated_insights,
            "content_ideas": content_ideas,
            "quality_score": quality_score,
        }

    def _is_hallucination(self, insight: str, context: dict[str, Any]) -> bool:
        suspicious = ["100% guaranteed", "확실히 1위", "무조건 바iral"]
        return any(s in insight for s in suspicious)

    def _calculate_quality(self, context: dict[str, Any], insights: list[str]) -> float:
        score = 0.0
        if context.get("videos"):
            score += 20
        if context.get("keywords"):
            score += 20
        if context.get("channel_analyses"):
            score += 20
        if insights:
            score += min(20, len(insights) * 3)
        if context.get("title_patterns"):
            score += 10
        if context.get("thumbnail_analysis"):
            score += 10
        return min(100, score)
