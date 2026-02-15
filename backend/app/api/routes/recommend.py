from fastapi import APIRouter, Depends, Request

from app.core.audit import log_event
from app.core.deps import get_cache, get_optional_user, get_session_store
from app.core.exceptions import FilmMatchError, NotFoundError
from app.core.logging import get_logger
from app.core.redis import RedisCache, SessionStore
from app.core.sanitize import sanitize_user_message
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
    req: Request,
    user: User | None = Depends(get_optional_user),
    cache: RedisCache = Depends(get_cache),
    session_store: SessionStore = Depends(get_session_store),
):
    # Sanitize user free-text input before it reaches Claude
    request.message = sanitize_user_message(request.message)

    user_id = str(user.id) if user else "anonymous"
    logger.info(
        "recommendation_requested",
        mode=request.mode,
        user_count=len(request.users),
        user_id=user_id,
    )
    log_event(
        "recommendation.created",
        user_id=user_id,
        ip=req.client.host if req.client else None,
        request_id=getattr(req.state, "request_id", None),
        detail=f"mode={request.mode} users={len(request.users)}",
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


@router.get("/{session_id}/receipt")
async def get_decision_receipt(
    session_id: str,
    session_store: SessionStore = Depends(get_session_store),
):
    """Generate a shareable decision receipt for a completed session."""
    session_data = await session_store.get(session_id)
    if session_data is None:
        raise NotFoundError("Session", session_id)

    prefs = session_data.get("preferences", {})
    users_data = prefs.get("users", [])
    member_names = [u.get("name", "Someone") for u in users_data]
    mode = prefs.get("mode", "solo")

    presented = session_data.get("presented_tmdb_ids", [])
    final = session_data.get("final_selection")
    reactions = session_data.get("reactions", [])
    complexity = session_data.get("complexity", {})

    liked = [r["tmdb_id"] for r in reactions if r.get("positive")]
    passed = [r["tmdb_id"] for r in reactions if not r.get("positive")]

    return {
        "session_id": session_id,
        "mode": mode,
        "members": member_names,
        "movies_considered": len(presented),
        "movies_liked": len(liked),
        "movies_passed": len(passed),
        "final_pick_tmdb_id": final,
        "complexity_tier": complexity.get("tier", "simple"),
        "turn_count": session_data.get("turn_count", 1),
        "shareable_text": _build_share_text(
            mode, member_names, final, len(presented)
        ),
    }


def _build_share_text(
    mode: str, members: list[str], final_tmdb_id: int | None, considered: int
) -> str:
    if mode == "group":
        names = " & ".join(members[:3])
        if len(members) > 3:
            names += f" + {len(members) - 3} more"
        base = f"{names} used FilmMatch AI to pick their movie night!"
    else:
        base = "I found my perfect movie with FilmMatch AI!"

    stats = f"Considered {considered} movies"
    if final_tmdb_id:
        stats += " and found the one."
    else:
        stats += "."

    return f"{base} {stats}"
