import json
import uuid
from pathlib import Path

import anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import RedisCache, SessionStore
from app.schemas.recommendation import (
    MovieSummary,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.tmdb_service import MovieCandidate, tmdb_service

logger = get_logger("ai_service")

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Singleton client — reused across requests
_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "filmmatch_system.md").read_text()


_cached_system_prompt: str | None = None


def _get_system_prompt() -> str:
    global _cached_system_prompt
    if _cached_system_prompt is None:
        _cached_system_prompt = _load_system_prompt()
    return _cached_system_prompt


def select_model(request: RecommendationRequest) -> str:
    """Route to the cheapest model that handles the request well."""
    num_users = len(request.users)

    if num_users >= 5:
        return "claude-sonnet-4-5-20250929"
    if num_users > 1:
        return "claude-sonnet-4-5-20250929"

    # Solo, simple request
    return "claude-haiku-4-5-20250514"


def _build_candidate_prompt(
    candidates: list[MovieCandidate],
    request: RecommendationRequest,
) -> str:
    """Build the user message with verified movie candidates."""
    movies_block = "\n".join(
        f"  {i + 1}. {c.to_prompt_string()}" for i, c in enumerate(candidates)
    )

    user_prefs = json.dumps(
        request.model_dump(exclude_none=True), indent=2, default=str
    )

    return f"""Here are {len(candidates)} verified movies to consider:

{movies_block}

User request:
{user_prefs}

IMPORTANT RULES:
- You MUST ONLY recommend movies from the numbered list above.
- Reference movies by their TMDB ID.
- Do NOT recommend any movie not in this list.

Respond in this exact JSON format:
{{
  "best_pick": {{
    "tmdb_id": <int>,
    "rationale": "<2-3 bullet reasons>",
    "match_score": <1-10>
  }},
  "additional_picks": [
    {{
      "tmdb_id": <int>,
      "rationale": "<one-line reason>",
      "match_score": <1-10>
    }}
  ],
  "narrow_question": "<one question to help narrow down further>",
  "overlap_summary": "<only for group mode: describe what the group shares>"
}}

Return 5 additional picks. Be concise. No spoilers."""


def _candidate_to_summary(
    candidate: MovieCandidate, match_score: float | None = None, rationale: str = ""
) -> MovieSummary:
    poster_url = (
        f"{settings.tmdb_image_base_url}/w500{candidate.poster_path}"
        if candidate.poster_path
        else None
    )
    backdrop_url = (
        f"{settings.tmdb_image_base_url}/w1280{candidate.backdrop_path}"
        if candidate.backdrop_path
        else None
    )
    year = candidate.release_date[:4] if candidate.release_date else None

    return MovieSummary(
        tmdb_id=candidate.tmdb_id,
        title=candidate.title,
        year=year,
        genres=candidate.genres,
        vote_average=candidate.vote_average,
        runtime=candidate.runtime,
        poster_url=poster_url,
        backdrop_url=backdrop_url,
        overview=candidate.overview,
        directors=candidate.director_names,
        cast=candidate.cast_names[:5],
        match_score=match_score,
        rationale=rationale,
    )


def _parse_ai_response(
    raw_text: str,
    candidates: list[MovieCandidate],
    session_id: str,
    model_used: str,
) -> RecommendationResponse:
    """Parse Claude's JSON response and validate against candidate set."""
    candidate_map = {c.tmdb_id: c for c in candidates}

    # Extract JSON from potential markdown code blocks
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("ai_response_parse_failed", raw=raw_text[:200])
        # Fallback: use top candidates by vote_average
        sorted_candidates = sorted(candidates, key=lambda c: c.vote_average, reverse=True)
        return RecommendationResponse(
            session_id=session_id,
            best_pick=_candidate_to_summary(sorted_candidates[0], rationale="Top rated match"),
            additional_picks=[
                _candidate_to_summary(c, rationale="Highly rated")
                for c in sorted_candidates[1:6]
            ],
            narrow_question="Would you prefer something more action-packed or more character-driven?",
            model_used=model_used,
        )

    # Validate best pick
    best_data = data.get("best_pick", {})
    best_id = best_data.get("tmdb_id")
    if best_id not in candidate_map:
        logger.warning("hallucinated_best_pick", tmdb_id=best_id)
        best_candidate = candidates[0]
    else:
        best_candidate = candidate_map[best_id]

    best_pick = _candidate_to_summary(
        best_candidate,
        match_score=best_data.get("match_score"),
        rationale=best_data.get("rationale", ""),
    )

    # Validate additional picks
    additional = []
    for pick_data in data.get("additional_picks", []):
        pick_id = pick_data.get("tmdb_id")
        if pick_id in candidate_map:
            additional.append(
                _candidate_to_summary(
                    candidate_map[pick_id],
                    match_score=pick_data.get("match_score"),
                    rationale=pick_data.get("rationale", ""),
                )
            )
        else:
            logger.warning("hallucinated_additional_pick", tmdb_id=pick_id)

    # Backfill if too few valid picks
    used_ids = {best_pick.tmdb_id} | {p.tmdb_id for p in additional}
    if len(additional) < 5:
        for c in candidates:
            if c.tmdb_id not in used_ids and len(additional) < 5:
                additional.append(_candidate_to_summary(c, rationale="Strong match"))
                used_ids.add(c.tmdb_id)

    return RecommendationResponse(
        session_id=session_id,
        best_pick=best_pick,
        additional_picks=additional,
        narrow_question=data.get("narrow_question"),
        overlap_summary=data.get("overlap_summary"),
        model_used=model_used,
    )


async def get_recommendation(
    request: RecommendationRequest,
    cache: RedisCache | None = None,
    session_store: SessionStore | None = None,
) -> RecommendationResponse:
    """Get movie recommendations using the hybrid TMDB + Claude approach."""
    session_id = str(uuid.uuid4())

    # Extract preferences from first user (solo) or merge (group)
    primary_user = request.users[0]
    all_likes = []
    all_dislikes = []
    for user in request.users:
        all_likes.extend(user.likes_genres)
        all_dislikes.extend(user.dislikes_genres)

    year_min = primary_user.year_range.min if primary_user.year_range else None
    year_max = primary_user.year_range.max if primary_user.year_range else None

    # Step 1: Fetch verified candidates from TMDB
    logger.info(
        "fetching_candidates",
        genres=all_likes,
        exclude=all_dislikes,
        year_range=(year_min, year_max),
    )
    candidates = await tmdb_service.fetch_candidates(
        genre_names=all_likes if all_likes else None,
        exclude_genre_names=all_dislikes if all_dislikes else None,
        year_min=year_min,
        year_max=year_max,
        max_candidates=30,
    )

    if not candidates:
        # Fallback to trending if no candidates match
        logger.warning("no_candidates_from_discover, falling_back_to_trending")
        trending = await tmdb_service.get_trending()
        for movie in trending[:20]:
            try:
                candidates.append(await tmdb_service.enrich_movie(movie))
            except Exception:
                continue

    if not candidates:
        from app.core.exceptions import ExternalServiceError
        raise ExternalServiceError("TMDB", "No movie candidates found")

    # Step 2: Have Claude rank and reason over verified candidates
    model = select_model(request)
    prompt = _build_candidate_prompt(candidates, request)

    logger.info("calling_claude", model=model, candidate_count=len(candidates))

    client = _get_client()
    response = await client.messages.create(
        model=model,
        max_tokens=1500,
        system=_get_system_prompt(),
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text
    total_tokens = response.usage.input_tokens + response.usage.output_tokens

    # Step 3: Parse and validate response
    result = _parse_ai_response(raw_text, candidates, session_id, model)

    # Store session in Redis for multi-turn
    if session_store:
        session_data = {
            "session_id": session_id,
            "preferences": request.model_dump(exclude_none=True),
            "candidate_tmdb_ids": [c.tmdb_id for c in candidates],
            "presented_tmdb_ids": [result.best_pick.tmdb_id]
            + [p.tmdb_id for p in result.additional_picks],
            "reactions": [],
            "turn_count": 1,
            "model_used": model,
            "total_tokens": total_tokens,
        }
        await session_store.set(session_id, session_data)

    logger.info(
        "recommendation_complete",
        session_id=session_id,
        model=model,
        tokens=total_tokens,
        candidates=len(candidates),
        picks=1 + len(result.additional_picks),
    )

    return result


async def refine_recommendation(
    session_id: str,
    feedback: str,
    keep_ids: list[int],
    reject_ids: list[int],
    session_store: SessionStore,
    cache: RedisCache | None = None,
) -> RecommendationResponse:
    """Refine recommendations based on user feedback."""
    session_data = await session_store.get(session_id)
    if session_data is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Session", session_id)

    # Build condensed context (not raw history)
    context = f"""Previous session context:
- User preferences: {json.dumps(session_data['preferences'])}
- Movies already suggested: {session_data['presented_tmdb_ids']}
- User kept (liked): {keep_ids}
- User rejected: {reject_ids}
- Current feedback: {feedback}

Provide refined recommendations from the original candidate set, excluding rejected movies.
Respond in the same JSON format as before."""

    model = session_data.get("model_used", "claude-haiku-4-5-20250514")
    client = _get_client()

    response = await client.messages.create(
        model=model,
        max_tokens=1500,
        system=_get_system_prompt(),
        messages=[{"role": "user", "content": context}],
    )

    raw_text = response.content[0].text

    # Re-fetch candidates that weren't rejected
    remaining_ids = set(session_data["candidate_tmdb_ids"]) - set(reject_ids)
    remaining_candidates = []
    for tmdb_id in remaining_ids:
        try:
            details = await tmdb_service.get_movie_details(tmdb_id)
            candidate = await tmdb_service.enrich_movie({"id": tmdb_id, **details})
            remaining_candidates.append(candidate)
        except Exception:
            continue

    result = _parse_ai_response(raw_text, remaining_candidates, session_id, model)

    # Update session
    session_data["turn_count"] = session_data.get("turn_count", 1) + 1
    session_data["presented_tmdb_ids"].extend(
        [result.best_pick.tmdb_id] + [p.tmdb_id for p in result.additional_picks]
    )
    await session_store.set(session_id, session_data)

    return result
