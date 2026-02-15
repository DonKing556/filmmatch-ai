import uuid
from datetime import datetime, timedelta, timezone

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger
from app.db.models import User

logger = get_logger("auth")

ALGORITHM = "HS256"


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "access"},
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise AuthenticationError()
        return payload
    except JWTError:
        raise AuthenticationError()


def create_magic_link_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(settings.magic_link_secret)
    return serializer.dumps(email, salt="magic-link")


def verify_magic_link_token(token: str) -> str:
    serializer = URLSafeTimedSerializer(settings.magic_link_secret)
    try:
        email = serializer.loads(
            token, salt="magic-link", max_age=settings.magic_link_expire_minutes * 60
        )
        return email
    except SignatureExpired:
        raise AuthenticationError("Magic link has expired")
    except BadSignature:
        raise AuthenticationError("Invalid magic link")


async def get_or_create_user(
    db: AsyncSession,
    email: str,
    auth_provider: str,
    display_name: str | None = None,
    auth_provider_id: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            display_name=display_name or email.split("@")[0],
            auth_provider=auth_provider,
            auth_provider_id=auth_provider_id,
        )
        db.add(user)
        await db.flush()
        logger.info("user_created", user_id=str(user.id), email=email)
    else:
        user.last_active_at = datetime.now(timezone.utc)
        logger.info("user_login", user_id=str(user.id), email=email)

    return user


def create_token_pair(user_id: str) -> dict:
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }
