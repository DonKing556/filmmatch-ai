from fastapi import APIRouter, Depends

from app.core.deps import get_cache, get_optional_user, get_session_store
from app.core.exceptions import FilmMatchError, NotFoundError
from app.core.logging import get_logger
from app.core.redis import RedisCache, SessionStore
from app.db.models import User
from app.schemas.recommendation import (
    NarrowRequest,
    ReactionRequest,
    RecommendationRequest,
    RecommendationResponse,
    SelectionRequest,
)
from app.services.ai_service import get_recommendation, refine_recommendation

logger = get_logger("recommend_routes")

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def create_recommendation(
    request: RecommendationRequest,
    user: User | None = Depends(get_optional_user),
    cache: RedisCache = Depends(get_cache),
    session_store: SessionStore = Depends(get_session_store),
):
    logger.info(
        "recommendation_requested",
        mode=request.mode,
        user_count=len(request.users),
        user_id=str(user.id) if user else "anonymous",
    )
    result = await get_recommendation(
        request, cache=cache, session_store=session_store
    )
    return result


@router.post("/{session_id}/refine", response_model=RecommendationResponse)
async def refine(
    session_id: str,
    request: NarrowRequest,
    session_store: SessionStore = Depends(get_session_store),
    cache: RedisCache = Depends(get_cache),
):
    result = await refine_recommendation(
        session_id=session_id,
        feedback=request.feedback,
        keep_ids=request.keep_tmdb_ids,
        reject_ids=request.reject_tmdb_ids,
        session_store=session_store,
        cache=cache,
    )
    return result


@router.post("/{session_id}/react")
async def react(
    session_id: str,
    request: ReactionRequest,
    session_store: SessionStore = Depends(get_session_store),
):
    session_data = await session_store.get(session_id)
    if session_data is None:
        raise NotFoundError("Session", session_id)

    session_data.setdefault("reactions", []).append(
        {
            "tmdb_id": request.tmdb_id,
            "positive": request.positive,
            "reason": request.reason,
        }
    )
    await session_store.set(session_id, session_data)
    return {"message": "Reaction recorded"}


@router.post("/{session_id}/select")
async def select_movie(
    session_id: str,
    request: SelectionRequest,
    session_store: SessionStore = Depends(get_session_store),
):
    session_data = await session_store.get(session_id)
    if session_data is None:
        raise NotFoundError("Session", session_id)

    session_data["final_selection"] = request.tmdb_id
    await session_store.set(session_id, session_data)

    logger.info(
        "movie_selected",
        session_id=session_id,
        tmdb_id=request.tmdb_id,
    )
    return {"message": "Selection recorded", "tmdb_id": request.tmdb_id}
