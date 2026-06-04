from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent


class EvaluationAgent(BaseAgent):
    """Post-hoc agent evaluation for quality, coverage, and hallucination risk."""

    name = "evaluation_agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        insights = context.get("insights", [])
        data = context
        quality_score = context.get("quality_score", 0)

        coverage_score = self._coverage_score(data)
        insight_quality = min(100, len(insights) * 12) if insights else 0
        data_richness = min(100, (
            (10 if data.get("videos") else 0)
            + (10 if data.get("keywords") else 0)
            + (10 if data.get("channel_analyses") else 0)
            + (10 if data.get("title_patterns") else 0)
            + (10 if data.get("thumbnail_analysis") else 0)
        ))
        hallucination_risk = self._hallucination_risk(insights)

        overall = round(
            quality_score * 0.4 + coverage_score * 0.3 + insight_quality * 0.2 + (100 - hallucination_risk) * 0.1,
            1,
        )

        evaluation = {
            "overall_score": overall,
            "quality_score": quality_score,
            "coverage_score": coverage_score,
            "insight_quality": insight_quality,
            "data_richness": data_richness,
            "hallucination_risk": hallucination_risk,
            "passed": overall >= 60 and hallucination_risk < 40,
            "recommendations": self._recommendations(overall, coverage_score, hallucination_risk),
        }

        self.log(f"Evaluation overall: {overall}")
        return {"evaluation": evaluation}

    def _coverage_score(self, data: dict[str, Any]) -> float:
        checks = [
            bool(data.get("videos")),
            bool(data.get("keywords")),
            bool(data.get("insights")),
            bool(data.get("report")),
            bool(data.get("plan")),
        ]
        return round(sum(checks) / len(checks) * 100, 1)

    def _hallucination_risk(self, insights: list[str]) -> float:
        risky_phrases = ["100%", "확실히", "무조건", "guaranteed", "definitely #1"]
        if not insights:
            return 50.0
        risky = sum(1 for i in insights if any(p in i for p in risky_phrases))
        return round(risky / len(insights) * 100, 1)

    def _recommendations(self, overall: float, coverage: float, hallucination: float) -> list[str]:
        recs = []
        if overall < 70:
            recs.append("추가 데이터 수집 또는 분석 유형 확장을 권장합니다.")
        if coverage < 60:
            recs.append("키워드/채널/제목 분석 커버리지가 부족합니다.")
        if hallucination > 30:
            recs.append("인사이트 검증 강화가 필요합니다.")
        if not recs:
            recs.append("분석 품질이 양호합니다.")
        return recs
