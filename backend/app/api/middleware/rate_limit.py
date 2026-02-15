"""Rate limiting middleware.

Applies per-IP rate limiting globally and exposes a dependency for
stricter per-route limits on expensive endpoints.
"""

from fastapi import Depends, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import RATE_LIMIT_HITS
from app.core.redis import RateLimiter, get_redis

logger = get_logger("rate_limit")

# Route-specific rate limits (requests per minute)
ROUTE_LIMITS: dict[str, int] = {
    "/api/v1/recommendations": 10,  # expensive Claude calls
    "/api/v1/auth/magic-link": 5,   # prevent email spam
}


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_identifier(request: Request) -> str:
    """Build a rate limit identifier: user ID if authenticated, else IP."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer ") and len(auth) > 20:
        # Use a hash of the token as identifier (avoids storing the token)
        import hashlib
        token_hash = hashlib.sha256(auth.encode()).hexdigest()[:16]
        return f"user:{token_hash}"
    return f"ip:{_get_client_ip(request)}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiting middleware.

    Checks per-identifier limits using Redis. Adds standard rate limit
    headers to every response. Returns 429 when limit is exceeded.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for health checks and OPTIONS
        if request.url.path == "/api/v1/health" or request.method == "OPTIONS":
            return await call_next(request)

        # Determine limit for this route
        path = request.url.path.rstrip("/")
        limit = ROUTE_LIMITS.get(path, settings.rate_limit_per_minute)
        identifier = _get_identifier(request)
        rate_key = f"{identifier}:{path}" if path in ROUTE_LIMITS else identifier

        try:
            redis_client = await get_redis()
            limiter = RateLimiter(redis_client)
            allowed = await limiter.check(rate_key, limit, window_seconds=60)
            remaining = await limiter.remaining(rate_key, limit)
        except Exception:
            # Fail-open: allow request if Redis is unavailable
            allowed = True
            remaining = limit

        if not allowed:
            RATE_LIMIT_HITS.labels(route=path).inc()
            logger.warning(
                "rate_limit_exceeded",
                identifier=identifier,
                path=path,
                limit=limit,
            )
            return JSONResponse(
                status_code=429,
                content={"error": f"Rate limit exceeded. Max {limit} requests per minute."},
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining - 1))
        return response
