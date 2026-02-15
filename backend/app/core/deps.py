from collections.abc import AsyncGenerator
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, credentials_exception
from app.core.redis import RedisCache, RateLimiter, SessionStore, get_redis
from app.db.models import User
from app.db.session import get_db
from app.services.auth_service import decode_token


async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception()

    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception()

    return user


async def get_optional_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_user(authorization=authorization, db=db)
    except Exception:
        return None


async def get_cache(
    r: aioredis.Redis = Depends(get_redis),
) -> RedisCache:
    return RedisCache(r)


async def get_session_store(
    r: aioredis.Redis = Depends(get_redis),
) -> SessionStore:
    return SessionStore(r)


async def get_rate_limiter(
    r: aioredis.Redis = Depends(get_redis),
) -> RateLimiter:
    return RateLimiter(r)
