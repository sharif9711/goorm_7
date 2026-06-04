from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


class TaskStore:
    """Redis-backed store for async analysis task results."""

    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def set_task(self, task_id: str, data: dict[str, Any], ttl: int = 86400) -> None:
        redis = await self.get_redis()
        await redis.setex(f"task:{task_id}", ttl, json.dumps(data, default=str))

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        redis = await self.get_redis()
        data = await redis.get(f"task:{task_id}")
        if data:
            return json.loads(data)
        return None

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()


task_store = TaskStore()
