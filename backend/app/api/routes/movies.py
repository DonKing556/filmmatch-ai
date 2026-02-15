from fastapi import APIRouter, Depends

from app.core.deps import get_cache
from app.core.logging import get_logger
from app.core.redis import RedisCache
from app.services.tmdb_service import tmdb_service

logger = get_logger("movie_routes")

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/trending")
async def get_trending(
    time_window: str = "week",
    cache: RedisCache = Depends(get_cache),
):
    cache_key = f"trending:{time_window}"
    cached = await cache.get_json(cache_key)
    if cached:
        return cached

    trending = await tmdb_service.get_trending(time_window)
    result = {
        "results": [
            {
                "tmdb_id": m["id"],
                "title": m.get("title", ""),
                "overview": m.get("overview", "")[:200],
                "release_date": m.get("release_date"),
                "vote_average": m.get("vote_average", 0),
                "poster_path": m.get("poster_path"),
                "backdrop_path": m.get("backdrop_path"),
            }
            for m in trending[:20]
        ]
    }

    await cache.set_json(cache_key, result, ttl_seconds=3600)
    return result


@router.get("/{tmdb_id}")
async def get_movie_details(
    tmdb_id: int,
    cache: RedisCache = Depends(get_cache),
):
    cache_key = f"movie:{tmdb_id}"
    cached = await cache.get_json(cache_key)
    if cached:
        return cached

    details = await tmdb_service.get_movie_details(tmdb_id)

    credits = details.get("credits", {})
    directors = [
        c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"
    ]
    cast = [
        {"name": c["name"], "character": c.get("character", "")}
        for c in credits.get("cast", [])[:10]
    ]

    result = {
        "tmdb_id": details["id"],
        "title": details.get("title", ""),
        "original_title": details.get("original_title"),
        "overview": details.get("overview", ""),
        "release_date": details.get("release_date"),
        "runtime": details.get("runtime"),
        "vote_average": details.get("vote_average", 0),
        "vote_count": details.get("vote_count", 0),
        "genres": [g["name"] for g in details.get("genres", [])],
        "poster_path": details.get("poster_path"),
        "backdrop_path": details.get("backdrop_path"),
        "original_language": details.get("original_language"),
        "directors": directors,
        "cast": cast,
    }

    await cache.set_json(cache_key, result, ttl_seconds=86400)
    return result
