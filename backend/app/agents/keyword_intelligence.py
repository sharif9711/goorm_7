from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.agents.base import BaseAgent


class KeywordIntelligenceAgent(BaseAgent):
    name = "keyword_intelligence_agent"

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "이", "그", "저", "것", "수", "등", "및", "를", "을", "의", "에", "가",
        "은", "는", "로", "으로", "와", "과", "도", "만", "에서",
    }

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        videos = context.get("videos", [])
        query = context.get("query", "").lower()

        word_counter: Counter = Counter()
        tag_counter: Counter = Counter()

        for video in videos:
            title_words = self._tokenize(video.get("title", ""))
            desc_words = self._tokenize(video.get("description", "")[:500])
            word_counter.update(title_words)
            word_counter.update(desc_words)

            for tag in video.get("tags", []):
                tag_counter[tag.lower()] += 1

        total = sum(word_counter.values()) or 1
        keywords: list[dict[str, Any]] = []

        for word, count in word_counter.most_common(50):
            if word in self.STOP_WORDS or len(word) < 2:
                continue
            growth_rate = 1.5 if query and query in word else 1.0
            competition = min(100, (count / total) * 1000)
            trend_score = count * growth_rate / (competition + 1) * 10
            keywords.append({
                "keyword": word,
                "frequency": count,
                "growth_rate": round(growth_rate, 2),
                "competition_score": round(competition, 2),
                "trend_score": round(trend_score, 2),
            })

        for tag, count in tag_counter.most_common(20):
            keywords.append({
                "keyword": tag,
                "frequency": count,
                "growth_rate": 1.2,
                "competition_score": round(count / max(len(videos), 1) * 10, 2),
                "trend_score": round(count * 1.2, 2),
            })

        keywords.sort(key=lambda x: x["trend_score"], reverse=True)
        self.log(f"Extracted {len(keywords)} keywords")
        return {"keywords": keywords[:30]}

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        words = re.findall(r"[\w가-힣]+", text)
        return [w for w in words if len(w) > 1]
