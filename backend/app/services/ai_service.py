import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

import anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import (
    CLAUDE_FALLBACK_TOTAL,
    CLAUDE_REQUESTS_TOTAL,
    RECOMMENDATION_LATENCY,
    RECOMMENDATIONS_TOTAL,
)
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


def _get_system_prompt_with_cache_control() -> list[dict]:
    """Return system prompt as a content block with Anthropic cache_control.

    This tells the Anthropic API to cache the system prompt across requests,
    saving ~90% on input tokens for repeated calls with the same system prompt.
    """
    return [
        {
            "type": "text",
            "text": _get_system_prompt(),
            "cache_control": {"type": "ephemeral"},
        }
    ]


# ---------------------------------------------------------------------------
# Complexity scoring & model routing
# ---------------------------------------------------------------------------

@dataclass
class ComplexityScore:
    score: int
    tier: str  # "simple", "moderate", "complex"
    model: str
    reasons: list[str]


def compute_complexity(request: RecommendationRequest) -> ComplexityScore:
    """Score request complexity to route to the right model tier.

    Scoring factors:
      +0  solo user, basic genres
      +2  per additional user beyond 1
      +1  per conflicting genre (liked by one, disliked by another)
      +1  constraints present (runtime, family-friendly, etc.)
      +1  free-text message included (requires more nuanced reasoning)
      +1  context fields set (occasion, energy, familiarity)
      +2  5+ users (large group dynamics)

    Tiers:
      0-2   → simple   → Haiku  (solo / simple group)
      3-5   → moderate → Sonnet (multi-user / constrained)
      6+    → complex  → Opus   (large groups / heavy constraints)
    """
    score = 0
    reasons: list[str] = []
    num_users = len(request.users)

    # Multi-user scoring
    if num_users > 1:
        extra = (num_users - 1) * 2
        score += extra
        reasons.append(f"{num_users} users (+{extra})")

    # Large group bonus
    if num_users >= 5:
        score += 2
        reasons.append("large group 5+ (+2)")

    # Conflicting genres across users
    if num_users > 1:
        all_likes = set()
        all_dislikes = set()
        for user in request.users:
            all_likes.update(g.lower() for g in user.likes_genres)
            all_dislikes.update(g.lower() for g in user.dislikes_genres)
        conflicts = all_likes & all_dislikes
        if conflicts:
            score += len(conflicts)
            reasons.append(f"{len(conflicts)} genre conflicts (+{len(conflicts)})")

    # Constraints
    primary = request.users[0]
    if primary.constraints:
        c = primary.constraints
        constraint_count = sum([
            c.max_runtime_min is not None,
            c.subtitles_ok is not None,
            c.streaming_services is not None and len(c.streaming_services) > 0,
            c.family_friendly is not None,
        ])
        if constraint_count > 0:
            score += constraint_count
            reasons.append(f"{constraint_count} constraints (+{constraint_count})")

    # Free-text message
    if request.message and len(request.message.strip()) > 20:
        score += 1
        reasons.append("free-text message (+1)")

    # Context fields
    if request.context:
        ctx = request.context
        ctx_count = sum([
            ctx.occasion is not None,
            ctx.energy is not None,
            ctx.familiarity is not None,
            ctx.want_something_new,
        ])
        if ctx_count > 0:
            score += ctx_count
            reasons.append(f"{ctx_count} context fields (+{ctx_count})")

    # Determine tier and model
    if score >= 6:
        tier = "complex"
        model = "claude-opus-4-6"
    elif score >= 3:
        tier = "moderate"
        model = "claude-sonnet-4-5-20250929"
    else:
        tier = "simple"
        model = "claude-haiku-4-5-20250514"

    return ComplexityScore(score=score, tier=tier, model=model, reasons=reasons)


def select_model(request: RecommendationRequest) -> str:
    """Route to the cheapest model that handles the request well."""
    return compute_complexity(request).model


# ---------------------------------------------------------------------------
# Recommendation pattern cache
# ---------------------------------------------------------------------------

PATTERN_CACHE_TTL = 21600  # 6 hours


def _normalize_cache_key(request: RecommendationRequest) -> str:
    """Build a deterministic cache key from normalized preferences.

    Sorts all list fields, lowercases strings, and hashes the result
    so identical preference sets always produce the same key.
    """
    normalized = {
        "mode": request.mode,
        "users": [],
    }
    for user in request.users:
        normalized["users"].append({
            "likes": sorted(g.lower().strip() for g in user.likes_genres),
            "dislikes": sorted(g.lower().strip() for g in user.dislikes_genres),
            "mood": sorted(m.lower().strip() for m in user.mood),
            "actors": sorted(a.lower().strip() for a in user.favorite_actors),
            "directors": sorted(d.lower().strip() for d in user.favorite_directors),
            "year_range": (
                (user.year_range.min, user.year_range.max)
                if user.year_range
                else None
            ),
        })

    if request.context:
        normalized["context"] = {
            "occasion": (request.context.occasion or "").lower(),
            "energy": (request.context.energy or "").lower(),
            "new": request.context.want_something_new,
        }

    key_str = json.dumps(normalized, sort_keys=True)
    digest = hashlib.sha256(key_str.encode()).hexdigest()[:16]
    return f"rec:pattern:{digest}"


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

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

    # Collect all dealbreakers across users
    all_dealbreakers = []
    for user in request.users:
        all_dealbreakers.extend(user.dealbreakers)

    dealbreaker_block = ""
    if all_dealbreakers:
        items = ", ".join(f'"{d}"' for d in all_dealbreakers)
        dealbreaker_block = f"\n\nDEALBREAKERS (Save me from...): [{items}]\nAVOID any movie that matches these dealbreakers.\n"

    return f"""Here are {len(candidates)} verified movies to consider:

{movies_block}

User request:
{user_prefs}{dealbreaker_block}

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


# ---------------------------------------------------------------------------
# Main recommendation flow
# ---------------------------------------------------------------------------

async def get_recommendation(
    request: RecommendationRequest,
    cache: RedisCache | None = None,
    session_store: SessionStore | None = None,
) -> RecommendationResponse:
    """Get movie recommendations using the hybrid TMDB + Claude approach."""
    session_id = str(uuid.uuid4())

    # Check pattern cache first
    cache_key = _normalize_cache_key(request)
    if cache:
        cached = await cache.get_json(cache_key)
        if cached:
            logger.info("pattern_cache_hit", cache_key=cache_key)
            cached["session_id"] = session_id
            result = RecommendationResponse(**cached)
            # Still store session for multi-turn even on cache hit
            if session_store:
                await session_store.set(session_id, {
                    "session_id": session_id,
                    "preferences": request.model_dump(exclude_none=True),
                    "candidate_tmdb_ids": [p.tmdb_id for p in result.additional_picks]
                    + [result.best_pick.tmdb_id],
                    "presented_tmdb_ids": [result.best_pick.tmdb_id]
                    + [p.tmdb_id for p in result.additional_picks],
                    "reactions": [],
                    "turn_count": 1,
                    "model_used": result.model_used,
                    "total_tokens": 0,
                    "from_cache": True,
                })
            return result

    # Extract preferences from first user (solo) or merge (group)
    all_likes = []
    all_dislikes = []
    for user in request.users:
        all_likes.extend(user.likes_genres)
        all_dislikes.extend(user.dislikes_genres)

    primary_user = request.users[0]
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

    # Step 2: Compute complexity and select model
    complexity = compute_complexity(request)
    model = complexity.model
    prompt = _build_candidate_prompt(candidates, request)

    logger.info(
        "calling_claude",
        model=model,
        candidate_count=len(candidates),
        complexity_score=complexity.score,
        complexity_tier=complexity.tier,
        complexity_reasons=complexity.reasons,
    )

    # Step 3: Call Claude with prompt caching on system prompt (with retry)
    import time as _time
    _start = _time.monotonic()

    client = _get_client()
    raw_text = None
    total_tokens = 0
    ai_failed = False

    for attempt in range(3):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=1500,
                system=_get_system_prompt_with_cache_control(),
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text
            total_tokens = response.usage.input_tokens + response.usage.output_tokens
            CLAUDE_REQUESTS_TOTAL.labels(model=model, status="success").inc()

            # Log cache savings if available
            cache_creation = getattr(response.usage, "cache_creation_input_tokens", 0) or 0
            cache_read = getattr(response.usage, "cache_read_input_tokens", 0) or 0
            if cache_creation or cache_read:
                logger.info(
                    "prompt_cache_stats",
                    cache_creation_tokens=cache_creation,
                    cache_read_tokens=cache_read,
                    savings_pct=round(cache_read / max(response.usage.input_tokens, 1) * 100, 1),
                )
            break
        except Exception as e:
            CLAUDE_REQUESTS_TOTAL.labels(model=model, status="error").inc()
            logger.error(
                "claude_api_error",
                model=model,
                attempt=attempt + 1,
                error=str(e),
            )
            if attempt < 2:
                import asyncio
                await asyncio.sleep(1.0 * (attempt + 1))
            else:
                ai_failed = True

    # Step 4: Parse and validate response (or fallback)
    if ai_failed or raw_text is None:
        CLAUDE_FALLBACK_TOTAL.inc()
        logger.warning("claude_fallback_activated", candidates=len(candidates))
        sorted_candidates = sorted(candidates, key=lambda c: c.vote_average, reverse=True)
        result = RecommendationResponse(
            session_id=session_id,
            best_pick=_candidate_to_summary(sorted_candidates[0], match_score=8.0, rationale="Top rated match (AI temporarily unavailable)"),
            additional_picks=[
                _candidate_to_summary(c, match_score=round(7.0 - i * 0.5, 1), rationale="Highly rated match")
                for i, c in enumerate(sorted_candidates[1:6])
            ],
            narrow_question="Would you prefer something more action-packed or more character-driven?",
            model_used=f"{model} (fallback)",
        )
    else:
        result = _parse_ai_response(raw_text, candidates, session_id, model)

    # Store in pattern cache for future identical requests
    if cache:
        cache_data = result.model_dump()
        cache_data.pop("session_id", None)
        await cache.set_json(cache_key, cache_data, ttl_seconds=PATTERN_CACHE_TTL)

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
            "complexity": {
                "score": complexity.score,
                "tier": complexity.tier,
                "reasons": complexity.reasons,
            },
        }
        await session_store.set(session_id, session_data)

    _elapsed = _time.monotonic() - _start
    RECOMMENDATION_LATENCY.labels(mode=request.mode).observe(_elapsed)
    RECOMMENDATIONS_TOTAL.labels(
        mode=request.mode, model=model, complexity_tier=complexity.tier
    ).inc()

    logger.info(
        "recommendation_complete",
        session_id=session_id,
        model=model,
        tokens=total_tokens,
        candidates=len(candidates),
        picks=1 + len(result.additional_picks),
        complexity_tier=complexity.tier,
        latency_seconds=round(_elapsed, 2),
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
        system=_get_system_prompt_with_cache_control(),
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
