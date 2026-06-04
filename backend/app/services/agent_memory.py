from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


class AgentMemoryService:
    """Redis-backed agent memory for cross-session context."""

    PREFIX = "agent_memory"
    TTL = 60 * 60 * 24 * 30  # 30 days

    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def _redis_client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    def _key(self, user_id: int) -> str:
        return f"{self.PREFIX}:user:{user_id}"

    async def add_analysis_memory(
        self,
        user_id: int,
        task_id: str,
        query: str,
        analysis_type: str,
        summary: str,
        keywords: list[str] | None = None,
    ) -> None:
        redis = await self._redis_client()
        entry = {
            "task_id": task_id,
            "query": query,
            "analysis_type": analysis_type,
            "summary": summary,
            "keywords": keywords or [],
        }
        await redis.lpush(self._key(user_id), json.dumps(entry, ensure_ascii=False))
        await redis.ltrim(self._key(user_id), 0, 49)
        await redis.expire(self._key(user_id), self.TTL)

    async def get_user_memory(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        redis = await self._redis_client()
        raw = await redis.lrange(self._key(user_id), 0, limit - 1)
        return [json.loads(item) for item in raw]

    async def search_memory(self, user_id: int, query: str, limit: int = 5) -> list[dict[str, Any]]:
        memories = await self.get_user_memory(user_id, limit=50)
        q = query.lower()
        matched = [m for m in memories if q in m.get("query", "").lower() or q in m.get("summary", "").lower()]
        return matched[:limit]
