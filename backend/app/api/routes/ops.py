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
from app.services.tmdb_service import tmdb_service

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


@router.post("/warmup")
async def warmup(cache: RedisCache = Depends(get_cache)):
    """Pre-populate Redis cache with trending movies from TMDB.

    Call this after deployment to ensure the first users get fast responses.
    """
    results = {"trending": 0, "errors": []}

    try:
        trending = await tmdb_service.get_trending()
        results["trending"] = len(trending)

        # Cache the trending list
        await cache.set_json("trending:weekly", trending, ttl_seconds=3600)

        # Pre-enrich top 20 movies (populates TMDB detail cache)
        enriched = 0
        for movie in trending[:20]:
            try:
                await tmdb_service.enrich_movie(movie)
                enriched += 1
            except Exception as e:
                results["errors"].append(f"enrich {movie.get('id')}: {e}")

        results["enriched"] = enriched
    except Exception as e:
        results["errors"].append(f"trending: {e}")

    logger.info("warmup_complete", **results)
    return {
        "status": "ok" if not results["errors"] else "partial",
        **results,
    }


@router.get("/launch-check")
async def launch_check(cache: RedisCache = Depends(get_cache)):
    """Comprehensive pre-launch readiness report.

    Checks all dependencies, caches, config, and critical endpoints.
    Returns a structured report suitable for launch go/no-go decisions.
    """
    report: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": settings.environment,
        "version": "0.3.0",
        "checks": {},
        "warnings": [],
    }

    # 1. Database
    try:
        from app.db.session import async_engine
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        report["checks"]["database"] = "ok"
    except Exception as e:
        report["checks"]["database"] = f"error: {e}"

    # 2. Redis
    try:
        redis = await get_redis()
        await redis.ping()
        report["checks"]["redis"] = "ok"
    except Exception as e:
        report["checks"]["redis"] = f"error: {e}"

    # 3. TMDB connectivity
    try:
        trending = await tmdb_service.get_trending()
        report["checks"]["tmdb"] = f"ok ({len(trending)} trending)"
    except Exception as e:
        report["checks"]["tmdb"] = f"error: {e}"

    # 4. Cache status
    try:
        cached_trending = await cache.get_json("trending:weekly")
        if cached_trending:
            report["checks"]["trending_cache"] = f"ok ({len(cached_trending)} movies)"
        else:
            report["checks"]["trending_cache"] = "empty (run /ops/warmup)"
            report["warnings"].append("Trending cache is empty — run POST /ops/warmup")
    except Exception:
        report["checks"]["trending_cache"] = "unavailable"

    # 5. Config validation
    if not settings.anthropic_api_key:
        report["warnings"].append("ANTHROPIC_API_KEY is not set")
    if not settings.tmdb_api_key:
        report["warnings"].append("TMDB_API_KEY is not set")
    if settings.jwt_secret_key == "change-me":
        report["warnings"].append("JWT_SECRET_KEY is still default — change for production")
    if settings.magic_link_secret == "change-me":
        report["warnings"].append("MAGIC_LINK_SECRET is still default — change for production")
    if not settings.sentry_dsn and settings.is_production:
        report["warnings"].append("SENTRY_DSN not set in production")

    report["checks"]["config"] = "ok" if not any(
        "not set" in w for w in report["warnings"]
    ) else "warnings"

    # Summary
    all_ok = all(
        v == "ok" or v.startswith("ok")
        for k, v in report["checks"].items()
        if k != "config"
    )
    report["ready"] = all_ok and len(report["warnings"]) == 0
    report["go_no_go"] = "GO" if report["ready"] else "NO-GO"

    return report
