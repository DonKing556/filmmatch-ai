"""Nightly TMDB sync — fetches trending and popular movies, persists to Movie table."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Movie
from app.db.session import async_session_factory
from app.services.tmdb_service import MovieCandidate, tmdb_service

logger = get_logger("sync")


def _candidate_to_dict(c: MovieCandidate) -> dict:
    """Convert a MovieCandidate to a dict for the Movie model."""
    return {
        "tmdb_id": c.tmdb_id,
        "title": c.title,
        "overview": c.overview,
        "release_date": c.release_date,
        "genres": c.genre_ids,
        "genre_names": c.genres,
        "vote_average": c.vote_average,
        "vote_count": c.vote_count,
        "popularity": c.popularity,
        "runtime": c.runtime,
        "poster_path": c.poster_path,
        "backdrop_path": c.backdrop_path,
        "original_language": c.original_language,
        "director_names": c.director_names,
        "cast_names": c.cast_names,
        "last_synced_at": datetime.now(timezone.utc),
    }


async def _upsert_movie(session: AsyncSession, candidate: MovieCandidate) -> None:
    """Insert or update a movie in the database."""
    movie_data = _candidate_to_dict(candidate)
    result = await session.execute(
        select(Movie).where(Movie.tmdb_id == candidate.tmdb_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        for key, value in movie_data.items():
            if key != "tmdb_id":
                setattr(existing, key, value)
    else:
        session.add(Movie(**movie_data))


async def sync_tmdb_catalog() -> dict:
    """Fetch trending + popular movies from TMDB and upsert into Movie table."""
    logger.info("sync_started")
    synced = 0
    errors = 0

    try:
        # Fetch from multiple sources
        trending = await tmdb_service.get_trending("week")
        discover_p1 = await tmdb_service.discover_movies(page=1)
        discover_p2 = await tmdb_service.discover_movies(page=2)

        # Merge and deduplicate
        seen_ids: set[int] = set()
        all_movies: list[dict] = []
        for movie in trending + discover_p1 + discover_p2:
            mid = movie["id"]
            if mid not in seen_ids:
                seen_ids.add(mid)
                all_movies.append(movie)

        # Enrich and persist
        async with async_session_factory() as session:
            for basic in all_movies:
                try:
                    candidate = await tmdb_service.enrich_movie(basic)
                    await _upsert_movie(session, candidate)
                    synced += 1
                except Exception as e:
                    logger.warning(
                        "sync_movie_failed",
                        tmdb_id=basic.get("id"),
                        error=str(e),
                    )
                    errors += 1

            await session.commit()

    except Exception as e:
        logger.error("sync_failed", error=str(e))

    logger.info("sync_completed", synced=synced, errors=errors)
    return {"synced": synced, "errors": errors}
