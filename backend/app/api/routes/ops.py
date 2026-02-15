"""Operations dashboard endpoints.

Provides internal health/readiness checks and operational stats
for monitoring dashboards and deployment tooling.
"""

import time

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import get_cache, get_session_store
from app.core.logging import get_logger
from app.core.redis import RedisCache, SessionStore, get_redis

logger = get_logger("ops")

router = APIRouter(prefix="/ops", tags=["operations"])

_start_time = time.monotonic()


@router.get("/readiness")
async def readiness():
    """Readiness probe — checks that all dependencies are reachable."""
    checks = {}

    # Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    # DB check (via SQLAlchemy)
    try:
        from app.db.session import async_engine
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "ready": all_ok,
        "checks": checks,
        "environment": settings.environment,
    }


@router.get("/stats")
async def stats(
    cache: RedisCache = Depends(get_cache),
    session_store: SessionStore = Depends(get_session_store),
):
    """Operational stats for the dashboard."""
    uptime = time.monotonic() - _start_time

    # Count active sessions in Redis
    active_sessions = 0
    try:
        redis = await get_redis()
        keys = await redis.keys("session:*")
        active_sessions = len(keys)
    except Exception:
        pass

    return {
        "uptime_seconds": round(uptime, 1),
        "version": "0.3.0",
        "environment": settings.environment,
        "active_sessions": active_sessions,
    }
