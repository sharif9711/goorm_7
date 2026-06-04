from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()


class OpenAIService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.vision_model = settings.OPENAI_VISION_MODEL

    async def generate_insights(self, context_data: dict[str, Any], query: str) -> list[str]:
        if not self.client:
            return self._fallback_insights(context_data, query)

        prompt = f"""YouTube 트렌드 분석 데이터를 기반으로 콘텐츠 제작자를 위한 인사이트 5-7개를 한국어로 작성하세요.
Query: {query}
Data summary: {json.dumps(context_data, ensure_ascii=False, default=str)[:8000]}

각 인사이트는 구체적이고 실행 가능해야 합니다."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a YouTube trend research expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""
        return [line.strip("- •").strip() for line in content.split("\n") if line.strip()]

    async def generate_content_ideas(self, context_data: dict[str, Any], query: str) -> dict[str, list[str]]:
        if not self.client:
            return self._fallback_content_ideas(query)

        prompt = f"""YouTube 트렌드 분석을 기반으로 콘텐츠 아이디어를 생성하세요.
Query: {query}
Data: {json.dumps(context_data, ensure_ascii=False, default=str)[:6000]}

JSON 형식으로 응답:
{{"shorts": ["아이디어1", ...], "longform": ["아이디어1", ...], "blog": ["아이디어1", ...]}}
각 카테고리당 20개씩 한국어로 작성."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a content strategist. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            return {
                "shorts": data.get("shorts", [])[:20],
                "longform": data.get("longform", [])[:20],
                "blog": data.get("blog", [])[:20],
            }
        except json.JSONDecodeError:
            return self._fallback_content_ideas(query)

    async def analyze_thumbnails(self, thumbnail_urls: list[str]) -> dict[str, Any]:
        if not self.client or not thumbnail_urls:
            return {"styles": [], "summary": "Vision analysis unavailable"}

        urls = thumbnail_urls[:5]
        content: list[dict[str, Any]] = [
            {"type": "text", "text": "Analyze these YouTube thumbnails. Return JSON with: styles (list), colors (list), text_usage (string), face_presence (string), summary (string in Korean)."}
        ]
        for url in urls:
            content.append({"type": "image_url", "image_url": {"url": url}})

        response = await self.client.chat.completions.create(
            model=self.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=1500,
        )
        raw = response.choices[0].message.content or "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"summary": raw, "styles": []}

    async def generate_report_markdown(self, context: dict[str, Any]) -> str:
        if not self.client:
            return self._fallback_report(context)

        prompt = f"""다음 YouTube 트렌드 분석 결과를 Markdown 리포트로 작성하세요.
{json.dumps(context, ensure_ascii=False, default=str)[:10000]}

포함 섹션: 요약, 키워드 트렌드, 채널 분석, 제목 패턴, 썸네일 인사이트, 콘텐츠 추천, 실행 가능한 다음 단계"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional YouTube trend analyst writing reports in Korean."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content or self._fallback_report(context)

    async def create_embedding(self, text: str) -> list[float]:
        if not self.client:
            return [0.0] * settings.EMBEDDING_DIMENSION
        response = await self.client.embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding

    def _fallback_insights(self, context_data: dict[str, Any], query: str) -> list[str]:
        keywords = context_data.get("keywords", [])[:3]
        kw_text = ", ".join(k.get("keyword", "") for k in keywords) if keywords else query
        return [
            f"'{query}' 관련 콘텐츠 수요가 증가하고 있습니다.",
            f"주요 키워드: {kw_text}",
            "숫자와 감정 유발 단어가 포함된 제목이 높은 CTR을 보입니다.",
            "썸네일에 인물 클로즈업과 대비가 강한 색상이 효과적입니다.",
            "쇼츠 형식의 요약 콘텐츠가 빠르게 성장하고 있습니다.",
        ]

    def _fallback_content_ideas(self, query: str) -> dict[str, list[str]]:
        base = [
            f"{query} 완벽 가이드 2026",
            f"{query} 초보자를 위한 5가지 팁",
            f"충격! {query}의 진실",
            f"{query} 실전 활용법",
            f"AI와 {query}의 미래",
        ]
        return {
            "shorts": [f"[쇼츠] {idea}" for idea in base * 4][:20],
            "longform": [f"[롱폼] {idea}" for idea in base * 4][:20],
            "blog": [f"[블로그] {idea}" for idea in base * 4][:20],
        }

    def _fallback_report(self, context: dict[str, Any]) -> str:
        query = context.get("query", "Analysis")
        return f"# {query} 트렌드 리포트\n\n## 요약\n분석이 완료되었습니다.\n\n## 데이터\n{json.dumps(context.get('data', {}), ensure_ascii=False, indent=2, default=str)[:3000]}"
