from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import (
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    create_magic_link_token,
    create_token_pair,
    decode_token,
    get_or_create_user,
    verify_magic_link_token,
)
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger

logger = get_logger("auth_routes")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/magic-link")
async def request_magic_link(request: MagicLinkRequest):
    token = create_magic_link_token(request.email)
    # In production, send this via email. For now, return it directly.
    logger.info("magic_link_created", email=request.email)
    return {
        "message": "Magic link created",
        "token": token,  # Remove in production — send via email instead
    }


@router.post("/verify", response_model=TokenResponse)
async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    email = verify_magic_link_token(request.token)
    user = await get_or_create_user(db, email=email, auth_provider="magic_link")
    return create_token_pair(str(user.id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type")
    return create_token_pair(payload["sub"])


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    # With stateless JWTs, logout is handled client-side by discarding tokens.
    # For enhanced security, we could add token to a Redis blacklist.
    return {"message": "Logged out"}
