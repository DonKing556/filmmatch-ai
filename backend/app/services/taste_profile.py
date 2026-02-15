"""Implicit taste profile builder.

Analyzes a user's watch history, ratings, and session reactions to compute
genre affinity scores, preferred actors/directors, and temporal patterns.
The computed profile can be injected into recommendation prompts so Claude
understands long-term preferences beyond what the user explicitly states.
"""

from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.redis import RedisCache
from app.db.models import WatchHistory, Movie

logger = get_logger("taste_profile")

TASTE_CACHE_TTL = 3600  # 1 hour


@dataclass
class GenreAffinity:
    genre: str
    score: float  # -1.0 (strong dislike) to +1.0 (strong like)
    interactions: int


@dataclass
class TasteProfile:
    user_id: str
    genre_affinities: list[GenreAffinity] = field(default_factory=list)
    preferred_decades: list[str] = field(default_factory=list)
    top_directors: list[str] = field(default_factory=list)
    top_actors: list[str] = field(default_factory=list)
    avg_rating: float | None = None
    total_interactions: int = 0

    def to_prompt_context(self) -> str:
        """Format as a concise string for injection into Claude prompts."""
        if self.total_interactions == 0:
            return ""

        parts = []

        # Top genre affinities
        liked = [g for g in self.genre_affinities if g.score > 0.2]
        disliked = [g for g in self.genre_affinities if g.score < -0.2]

        if liked:
            top = sorted(liked, key=lambda g: g.score, reverse=True)[:5]
            parts.append(
                "Implicit genre preferences (from history): "
                + ", ".join(f"{g.genre} ({g.score:+.1f})" for g in top)
            )

        if disliked:
            bottom = sorted(disliked, key=lambda g: g.score)[:3]
            parts.append(
                "Genres they tend to avoid: "
                + ", ".join(f"{g.genre} ({g.score:+.1f})" for g in bottom)
            )

        if self.preferred_decades:
            parts.append(f"Preferred eras: {', '.join(self.preferred_decades)}")

        if self.top_directors:
            parts.append(f"Favorite directors: {', '.join(self.top_directors[:3])}")

        if self.top_actors:
            parts.append(f"Favorite actors: {', '.join(self.top_actors[:3])}")

        return "\n".join(parts)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "genre_affinities": [
                {"genre": g.genre, "score": round(g.score, 2), "interactions": g.interactions}
                for g in self.genre_affinities
            ],
            "preferred_decades": self.preferred_decades,
            "top_directors": self.top_directors,
            "top_actors": self.top_actors,
            "avg_rating": round(self.avg_rating, 1) if self.avg_rating else None,
            "total_interactions": self.total_interactions,
        }


async def compute_taste_profile(
    user_id: str,
    db: AsyncSession,
    cache: RedisCache | None = None,
) -> TasteProfile:
    """Compute a user's implicit taste profile from their interaction history.

    Scoring logic per interaction:
      - watchlist add:   +0.3 per genre
      - watched:         +0.5 per genre
      - rating >= 7:     +0.8 per genre
      - rating 5-6:      +0.2 per genre
      - rating <= 4:     -0.5 per genre
      - dismissed:       -0.3 per genre
    """
    cache_key = f"taste:{user_id}"

    # Check cache
    if cache:
        cached = await cache.get_json(cache_key)
        if cached:
            return TasteProfile(
                user_id=cached["user_id"],
                genre_affinities=[
                    GenreAffinity(**g) for g in cached["genre_affinities"]
                ],
                preferred_decades=cached["preferred_decades"],
                top_directors=cached["top_directors"],
                top_actors=cached["top_actors"],
                avg_rating=cached["avg_rating"],
                total_interactions=cached["total_interactions"],
            )

    # Fetch watch history with movie details
    result = await db.execute(
        select(WatchHistory, Movie)
        .join(Movie, WatchHistory.tmdb_id == Movie.tmdb_id, isouter=True)
        .where(WatchHistory.user_id == user_id)
        .order_by(WatchHistory.created_at.desc())
        .limit(200)
    )
    rows = result.all()

    if not rows:
        return TasteProfile(user_id=user_id)

    # Accumulate genre scores
    genre_scores: dict[str, float] = defaultdict(float)
    genre_counts: dict[str, int] = defaultdict(int)
    decade_counts: dict[str, int] = defaultdict(int)
    director_counts: dict[str, int] = defaultdict(int)
    actor_counts: dict[str, int] = defaultdict(int)
    ratings: list[int] = []

    for history, movie in rows:
        if movie is None or not movie.genre_names:
            continue

        # Determine score weight based on interaction type
        weight = 0.0
        if history.status == "watchlist":
            weight = 0.3
        elif history.status == "watched":
            weight = 0.5
        elif history.status == "dismissed":
            weight = -0.3

        # Override with rating if present
        if history.rating is not None:
            ratings.append(history.rating)
            if history.rating >= 7:
                weight = 0.8
            elif history.rating >= 5:
                weight = 0.2
            else:
                weight = -0.5

        # Apply to genres
        for genre_name in movie.genre_names:
            genre_scores[genre_name] += weight
            genre_counts[genre_name] += 1

        # Track decade
        if movie.release_date and len(movie.release_date) >= 4:
            decade = movie.release_date[:3] + "0s"
            decade_counts[decade] += 1

        # Track directors/actors
        if movie.director_names:
            for d in movie.director_names:
                director_counts[d] += 1
        if movie.cast_names:
            for a in movie.cast_names[:3]:  # top 3 billed
                actor_counts[a] += 1

    # Normalize genre scores to [-1, 1] range
    affinities = []
    for genre, raw_score in genre_scores.items():
        count = genre_counts[genre]
        normalized = max(-1.0, min(1.0, raw_score / max(count, 1)))
        affinities.append(GenreAffinity(genre=genre, score=normalized, interactions=count))
    affinities.sort(key=lambda g: g.score, reverse=True)

    # Top decades (at least 2 interactions)
    preferred_decades = sorted(
        [d for d, c in decade_counts.items() if c >= 2],
        key=lambda d: decade_counts[d],
        reverse=True,
    )[:3]

    # Top directors (at least 2 movies)
    top_directors = sorted(
        [d for d, c in director_counts.items() if c >= 2],
        key=lambda d: director_counts[d],
        reverse=True,
    )[:5]

    # Top actors (at least 2 movies)
    top_actors = sorted(
        [a for a, c in actor_counts.items() if c >= 2],
        key=lambda a: actor_counts[a],
        reverse=True,
    )[:5]

    avg_rating = sum(ratings) / len(ratings) if ratings else None

    profile = TasteProfile(
        user_id=user_id,
        genre_affinities=affinities,
        preferred_decades=preferred_decades,
        top_directors=top_directors,
        top_actors=top_actors,
        avg_rating=avg_rating,
        total_interactions=len(rows),
    )

    # Cache the result
    if cache:
        await cache.set_json(cache_key, profile.to_dict(), ttl_seconds=TASTE_CACHE_TTL)

    logger.info(
        "taste_profile_computed",
        user_id=user_id,
        interactions=len(rows),
        genres=len(affinities),
    )

    return profile
