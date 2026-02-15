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
        # Verify connectivity — log warning but don't crash
        try:
            await _redis_client.ping()
        except Exception:
            logger.warning("redis_unavailable", url=settings.redis_url)
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
        try:
            data = await self.client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception:
            logger.warning("redis_get_failed", key=key)
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        try:
            await self.client.set(key, json.dumps(value), ex=ttl_seconds)
        except Exception:
            logger.warning("redis_set_failed", key=key)

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except Exception:
            logger.warning("redis_delete_failed", key=key)

    async def increment(self, key: str, ttl_seconds: int = 60) -> int:
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl_seconds)
            results = await pipe.execute()
            return results[0]
        except Exception:
            logger.warning("redis_increment_failed", key=key)
            return 1


class SessionStore:
    """Redis-backed session store for active recommendation sessions.

    Falls back to an in-memory dict when Redis is unavailable so that
    single-request flows still work (multi-turn will be lost on restart).
    """

    PREFIX = "session:"
    TTL = 1800  # 30 minutes

    def __init__(self, client: redis.Redis):
        self.client = client
        self._fallback: dict[str, dict] = {}

    def _key(self, session_id: str) -> str:
        return f"{self.PREFIX}{session_id}"

    async def get(self, session_id: str) -> dict | None:
        try:
            data = await self.client.get(self._key(session_id))
            if data is None:
                return self._fallback.get(session_id)
            return json.loads(data)
        except Exception:
            logger.warning("session_get_failed", session_id=session_id)
            return self._fallback.get(session_id)

    async def set(self, session_id: str, data: dict) -> None:
        self._fallback[session_id] = data
        try:
            await self.client.set(
                self._key(session_id), json.dumps(data), ex=self.TTL
            )
        except Exception:
            logger.warning("session_set_failed", session_id=session_id)

    async def extend(self, session_id: str) -> None:
        try:
            await self.client.expire(self._key(session_id), self.TTL)
        except Exception:
            logger.warning("session_extend_failed", session_id=session_id)

    async def delete(self, session_id: str) -> None:
        self._fallback.pop(session_id, None)
        try:
            await self.client.delete(self._key(session_id))
        except Exception:
            logger.warning("session_delete_failed", session_id=session_id)


class RateLimiter:
    """Redis-backed sliding window rate limiter.

    When Redis is unavailable, allows all requests (fail-open).
    """

    PREFIX = "ratelimit:"

    def __init__(self, client: redis.Redis):
        self.client = client

    async def check(self, identifier: str, limit: int, window_seconds: int = 60) -> bool:
        try:
            key = f"{self.PREFIX}{identifier}"
            count = await self.client.get(key)
            if count is not None and int(count) >= limit:
                return False
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            await pipe.execute()
            return True
        except Exception:
            logger.warning("rate_limiter_failed", identifier=identifier)
            return True  # fail-open

    async def remaining(self, identifier: str, limit: int) -> int:
        try:
            key = f"{self.PREFIX}{identifier}"
            count = await self.client.get(key)
            if count is None:
                return limit
            return max(0, limit - int(count))
        except Exception:
            logger.warning("rate_limiter_remaining_failed", identifier=identifier)
            return limit
