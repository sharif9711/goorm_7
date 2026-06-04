from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.agents.base import BaseAgent

CLICKBAIT_PATTERNS = [
    (r"충격", "감정 유발 - 충격"),
    (r"실화", "감정 유발 - 실화"),
    (r"AI", "AI 키워드"),
    (r"\d+", "숫자 사용"),
    (r"방법|하는\s?법|가이드|튜토리얼", "How-to 패턴"),
    (r"왜|어떻게|무엇", "질문형"),
    (r"최고|베스트|top", "순위/최고"),
    (r"비밀|숨겨진|모르는", "호기심 유발"),
    (r"vs|대결|비교", "비교형"),
    (r"!\?", "강조 부호"),
]


class TitlePatternAgent(BaseAgent):
    name = "title_pattern_agent"

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        videos = context.get("videos", [])
        pattern_counter: Counter = Counter()
        structures: list[str] = []

        for video in videos:
            title = video.get("title", "")
            for pattern, label in CLICKBAIT_PATTERNS:
                if re.search(pattern, title, re.IGNORECASE):
                    pattern_counter[label] += 1

            if "|" in title:
                structures.append("파이프 구분 (Topic | Hook)")
            elif re.search(r"^\d+", title):
                structures.append("숫자 시작")
            elif "?" in title or "？" in title:
                structures.append("질문형 제목")
            elif len(title) <= 40:
                structures.append("짧은 제목 (40자 이하)")
            else:
                structures.append("긴 설명형 제목")

        structure_counter = Counter(structures)
        top_patterns = [
            {"pattern": name, "count": count, "percentage": round(count / max(len(videos), 1) * 100, 1)}
            for name, count in pattern_counter.most_common(10)
        ]
        top_structures = [
            {"structure": name, "count": count}
            for name, count in structure_counter.most_common(5)
        ]

        self.log(f"Found {len(top_patterns)} title patterns")
        return {"title_patterns": top_patterns, "title_structures": top_structures}
