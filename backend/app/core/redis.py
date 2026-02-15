import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("redis")

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


class RedisCache:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def get_json(self, key: str) -> Any | None:
        data = await self.client.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        await self.client.set(key, json.dumps(value), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def increment(self, key: str, ttl_seconds: int = 60) -> int:
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl_seconds)
        results = await pipe.execute()
        return results[0]


class SessionStore:
    """Redis-backed session store for active recommendation sessions."""

    PREFIX = "session:"
    TTL = 1800  # 30 minutes

    def __init__(self, client: redis.Redis):
        self.client = client

    def _key(self, session_id: str) -> str:
        return f"{self.PREFIX}{session_id}"

    async def get(self, session_id: str) -> dict | None:
        data = await self.client.get(self._key(session_id))
        if data is None:
            return None
        return json.loads(data)

    async def set(self, session_id: str, data: dict) -> None:
        await self.client.set(
            self._key(session_id), json.dumps(data), ex=self.TTL
        )

    async def extend(self, session_id: str) -> None:
        await self.client.expire(self._key(session_id), self.TTL)

    async def delete(self, session_id: str) -> None:
        await self.client.delete(self._key(session_id))


class RateLimiter:
    """Redis-backed sliding window rate limiter."""

    PREFIX = "ratelimit:"

    def __init__(self, client: redis.Redis):
        self.client = client

    async def check(self, identifier: str, limit: int, window_seconds: int = 60) -> bool:
        key = f"{self.PREFIX}{identifier}"
        count = await self.client.get(key)
        if count is not None and int(count) >= limit:
            return False
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        await pipe.execute()
        return True

    async def remaining(self, identifier: str, limit: int) -> int:
        key = f"{self.PREFIX}{identifier}"
        count = await self.client.get(key)
        if count is None:
            return limit
        return max(0, limit - int(count))
