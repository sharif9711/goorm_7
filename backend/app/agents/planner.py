from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner_agent"

    ANALYSIS_PLANS: dict[str, list[str]] = {
        "keyword_search": [
            "YouTube 검색 수행",
            "영상 및 채널 데이터 수집",
            "키워드 분석",
            "제목 패턴 분석",
            "GPT 인사이트 생성",
            "리포트 생성",
        ],
        "trending": [
            "급상승 영상 수집",
            "조회수/댓글/좋아요 증가율 분석",
            "트렌드 점수 계산",
            "인사이트 생성",
            "리포트 생성",
        ],
        "channel": [
            "채널 정보 수집",
            "성장률 분석",
            "업로드 빈도 분석",
            "평균 조회수 분석",
            "인사이트 생성",
            "리포트 생성",
        ],
        "competitor": [
            "사용자 채널 분석",
            "경쟁 채널 수집",
            "Gap Analysis",
            "비교 차트 데이터 생성",
            "인사이트 생성",
            "리포트 생성",
        ],
        "title": [
            "영상 제목 수집",
            "제목 구조 분석",
            "클릭 유도 패턴 분석",
            "Top Patterns 추출",
            "리포트 생성",
        ],
        "thumbnail": [
            "썸네일 URL 수집",
            "Vision 모델 분석",
            "스타일 패턴 추출",
            "리포트 생성",
        ],
        "content_ideas": [
            "트렌드 데이터 수집",
            "키워드/제목/채널 분석",
            "콘텐츠 아이디어 생성",
            "품질 검증",
            "리포트 생성",
        ],
        "full": [
            "검색 수행",
            "채널 분석",
            "키워드 분석",
            "제목 분석",
            "썸네일 분석",
            "경쟁 분석",
            "인사이트 생성",
            "품질 검증",
            "리포트 생성",
        ],
    }

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        analysis_type = context.get("analysis_type", "keyword_search")
        query = context.get("query", "")
        plan = self.ANALYSIS_PLANS.get(analysis_type, self.ANALYSIS_PLANS["keyword_search"])

        if query:
            plan = [f"'{query}' 키워드로 {step}" for step in plan]

        self.log(f"Created plan with {len(plan)} steps for {analysis_type}")
        return {"plan": plan, "analysis_type": analysis_type}
