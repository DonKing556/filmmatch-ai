from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_cache, get_current_user
from app.core.redis import RedisCache
from app.db.models import User, UserPreferences, WatchHistory
from app.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.user import PreferencesUpdate, WatchHistoryItem, WatchlistAdd
from app.services.taste_profile import compute_taste_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at.isoformat(),
    )


@router.patch("/me/preferences")
async def update_preferences(
    update: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    )
    prefs = result.scalar_one_or_none()

    if prefs is None:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)

    update_data = update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(prefs, key, value)

    return {"message": "Preferences updated"}


@router.get("/me/history")
async def get_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: str | None = None,
    limit: int = 50,
):
    query = select(WatchHistory).where(WatchHistory.user_id == user.id)
    if status:
        query = query.where(WatchHistory.status == status)
    query = query.order_by(WatchHistory.created_at.desc()).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return [
        WatchHistoryItem(
            tmdb_id=item.tmdb_id,
            status=item.status,
            rating=item.rating,
            created_at=item.created_at.isoformat(),
        )
        for item in items
    ]


@router.post("/me/watchlist")
async def add_to_watchlist(
    request: WatchlistAdd,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = WatchHistory(
        user_id=user.id,
        tmdb_id=request.tmdb_id,
        status=request.status,
    )
    db.add(entry)
    return {"message": "Added to watchlist"}


@router.get("/me/taste-profile")
async def get_taste_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
):
    profile = await compute_taste_profile(
        user_id=str(user.id), db=db, cache=cache
    )
    return profile.to_dict()


@router.delete("/me/watchlist/{tmdb_id}")
async def remove_from_watchlist(
    tmdb_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WatchHistory).where(
            WatchHistory.user_id == user.id,
            WatchHistory.tmdb_id == tmdb_id,
            WatchHistory.status == "watchlist",
        )
    )
    entry = result.scalar_one_or_none()
    if entry:
        await db.delete(entry)
    return {"message": "Removed from watchlist"}
