from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.core.metrics import TMDB_REQUESTS_TOTAL

logger = get_logger("tmdb")

# TMDB genre ID mapping
GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western",
}

GENRE_NAME_TO_ID = {v.lower(): k for k, v in GENRE_MAP.items()}

# Map moods to TMDB genre boosts and sort strategies
MOOD_TO_GENRES: dict[str, list[int]] = {
    "feel-good": [35, 10751, 16],        # Comedy, Family, Animation
    "intense": [28, 53, 10752],           # Action, Thriller, War
    "mind-bending": [878, 9648, 14],      # Sci-Fi, Mystery, Fantasy
    "emotional": [18, 10749],             # Drama, Romance
    "relaxing": [35, 10751, 16],          # Comedy, Family, Animation
    "adventurous": [12, 28, 14],          # Adventure, Action, Fantasy
    "dark": [27, 53, 80],                 # Horror, Thriller, Crime
    "funny": [35, 16],                    # Comedy, Animation
    "romantic": [10749, 18, 35],          # Romance, Drama, Comedy
    "suspenseful": [53, 9648, 80],        # Thriller, Mystery, Crime
    "nostalgic": [12, 10751, 14],         # Adventure, Family, Fantasy
    "inspirational": [18, 36, 10752],     # Drama, History, War
}

MOOD_TO_SORT: dict[str, str] = {
    "feel-good": "vote_average.desc",
    "intense": "popularity.desc",
    "mind-bending": "vote_average.desc",
    "emotional": "vote_average.desc",
    "relaxing": "vote_average.desc",
    "adventurous": "popularity.desc",
    "dark": "vote_average.desc",
    "funny": "popularity.desc",
    "romantic": "vote_average.desc",
    "suspenseful": "popularity.desc",
    "nostalgic": "vote_average.desc",
    "inspirational": "vote_average.desc",
}


@dataclass
class MovieCandidate:
    tmdb_id: int
    title: str
    overview: str
    release_date: str | None
    genres: list[str]
    genre_ids: list[int]
    vote_average: float
    vote_count: int
    popularity: float
    runtime: int | None
    poster_path: str | None
    backdrop_path: str | None
    original_language: str
    director_names: list[str]
    cast_names: list[str]

    def to_prompt_string(self) -> str:
        genres_str = ", ".join(self.genres)
        cast_str = ", ".join(self.cast_names[:5])
        directors_str = ", ".join(self.director_names) if self.director_names else "Unknown"
        year = self.release_date[:4] if self.release_date else "Unknown"
        runtime_str = f"{self.runtime} min" if self.runtime else "Unknown"
        return (
            f"[TMDB ID: {self.tmdb_id}] {self.title} ({year}) | "
            f"Genres: {genres_str} | Rating: {self.vote_average}/10 | "
            f"Runtime: {runtime_str} | Director: {directors_str} | "
            f"Cast: {cast_str} | "
            f"Plot: {self.overview[:200]}"
        )


class TMDBService:
    def __init__(self):
        self.base_url = settings.tmdb_base_url
        self.api_key = settings.tmdb_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                params={"api_key": self.api_key},
                timeout=10.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _get(self, endpoint: str, params: dict | None = None, retries: int = 2) -> dict:
        client = await self._get_client()
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = await client.get(endpoint, params=params or {})
                response.raise_for_status()
                TMDB_REQUESTS_TOTAL.labels(endpoint=endpoint, status="success").inc()
                return response.json()
            except httpx.HTTPStatusError as e:
                TMDB_REQUESTS_TOTAL.labels(endpoint=endpoint, status=str(e.response.status_code)).inc()
                logger.error(
                    "tmdb_api_error",
                    endpoint=endpoint,
                    status=e.response.status_code,
                    attempt=attempt + 1,
                )
                # Don't retry client errors (4xx)
                if e.response.status_code < 500:
                    raise ExternalServiceError("TMDB", f"HTTP {e.response.status_code}")
                last_error = e
            except httpx.RequestError as e:
                TMDB_REQUESTS_TOTAL.labels(endpoint=endpoint, status="connection_error").inc()
                logger.error(
                    "tmdb_connection_error",
                    endpoint=endpoint,
                    error=str(e),
                    attempt=attempt + 1,
                )
                last_error = e

            # Brief back-off before retry
            if attempt < retries:
                import asyncio
                await asyncio.sleep(0.5 * (attempt + 1))

        raise ExternalServiceError("TMDB", f"Failed after {retries + 1} attempts: {last_error}")

    def _resolve_genre_ids(self, genre_names: list[str]) -> list[int]:
        ids = []
        for name in genre_names:
            genre_id = GENRE_NAME_TO_ID.get(name.lower())
            if genre_id:
                ids.append(genre_id)
        return ids

    async def discover_movies(
        self,
        genre_ids: list[int] | None = None,
        exclude_genre_ids: list[int] | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        vote_average_min: float = 5.5,
        sort_by: str = "vote_average.desc",
        page: int = 1,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "vote_average.gte": str(vote_average_min),
            "vote_count.gte": "50",
            "page": str(page),
            "include_adult": "false",
        }
        if genre_ids:
            params["with_genres"] = ",".join(str(g) for g in genre_ids)
        if exclude_genre_ids:
            params["without_genres"] = ",".join(str(g) for g in exclude_genre_ids)
        if year_min:
            params["primary_release_date.gte"] = f"{year_min}-01-01"
        if year_max:
            params["primary_release_date.lte"] = f"{year_max}-12-31"

        data = await self._get("/discover/movie", params)
        return data.get("results", [])

    async def search_movies(self, query: str, page: int = 1) -> list[dict]:
        data = await self._get("/search/movie", {"query": query, "page": str(page)})
        return data.get("results", [])

    async def get_trending(self, time_window: str = "week") -> list[dict]:
        data = await self._get(f"/trending/movie/{time_window}")
        return data.get("results", [])

    async def get_movie_details(self, tmdb_id: int) -> dict:
        return await self._get(
            f"/movie/{tmdb_id}",
            {"append_to_response": "credits,keywords"},
        )

    async def get_movie_credits(self, tmdb_id: int) -> dict:
        return await self._get(f"/movie/{tmdb_id}/credits")

    async def enrich_movie(self, basic_movie: dict) -> MovieCandidate:
        tmdb_id = basic_movie["id"]
        details = await self.get_movie_details(tmdb_id)

        genre_ids = [g["id"] for g in details.get("genres", [])]
        genre_names = [g["name"] for g in details.get("genres", [])]

        credits = details.get("credits", {})
        directors = [
            c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"
        ]
        cast = [c["name"] for c in credits.get("cast", [])[:10]]

        return MovieCandidate(
            tmdb_id=tmdb_id,
            title=details.get("title", ""),
            overview=details.get("overview", ""),
            release_date=details.get("release_date"),
            genres=genre_names,
            genre_ids=genre_ids,
            vote_average=details.get("vote_average", 0),
            vote_count=details.get("vote_count", 0),
            popularity=details.get("popularity", 0),
            runtime=details.get("runtime"),
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            original_language=details.get("original_language", "en"),
            director_names=directors,
            cast_names=cast,
        )

    async def fetch_candidates(
        self,
        genre_names: list[str] | None = None,
        exclude_genre_names: list[str] | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        mood: list[str] | None = None,
        max_candidates: int = 40,
    ) -> list[MovieCandidate]:
        genre_ids = self._resolve_genre_ids(genre_names) if genre_names else None
        exclude_ids = self._resolve_genre_ids(exclude_genre_names) if exclude_genre_names else None

        # Build mood-based genre boost and sort
        mood_genre_ids: set[int] = set()
        sort_by = "vote_average.desc"
        if mood:
            for m in mood:
                key = m.lower().strip()
                mood_genre_ids.update(MOOD_TO_GENRES.get(key, []))
                sort_by = MOOD_TO_SORT.get(key, sort_by)

        # Primary discover: user genre preferences
        discover_results = await self.discover_movies(
            genre_ids=genre_ids,
            exclude_genre_ids=exclude_ids,
            year_min=year_min,
            year_max=year_max,
            sort_by=sort_by,
        )

        # Secondary discover: mood-based genres (different pool)
        mood_results: list[dict] = []
        if mood_genre_ids:
            # Combine mood genres with user genres for a mood-flavored query
            combined_genres = list(mood_genre_ids)
            if genre_ids:
                combined_genres = list(set(combined_genres) | set(genre_ids))
            mood_results = await self.discover_movies(
                genre_ids=combined_genres,
                exclude_genre_ids=exclude_ids,
                year_min=year_min,
                year_max=year_max,
                sort_by=sort_by,
                page=2,  # Different page for variety
            )

        # Also fetch trending for freshness
        trending_results = await self.get_trending()

        # Merge and deduplicate — mood results first for priority
        seen_ids: set[int] = set()
        merged: list[dict] = []
        for movie in mood_results + discover_results + trending_results:
            mid = movie["id"]
            if mid not in seen_ids:
                seen_ids.add(mid)
                merged.append(movie)

        # Filter out excluded genres from trending/mood results
        if exclude_ids:
            merged = [
                m for m in merged
                if not set(m.get("genre_ids", [])) & set(exclude_ids)
            ]

        # Score movies by mood relevance
        if mood_genre_ids:
            def mood_score(movie: dict) -> float:
                movie_genres = set(movie.get("genre_ids", []))
                overlap = len(movie_genres & mood_genre_ids)
                return overlap + movie.get("vote_average", 0) / 10
            merged.sort(key=mood_score, reverse=True)

        # Take top N
        merged = merged[:max_candidates]

        # Enrich top candidates with full details
        candidates = []
        for movie in merged[:max_candidates]:
            try:
                candidate = await self.enrich_movie(movie)
                candidates.append(candidate)
            except Exception:
                logger.warning("enrich_failed", tmdb_id=movie.get("id"))
                continue

        logger.info(
            "candidates_fetched",
            count=len(candidates),
            mood=mood,
            genre_ids=genre_ids,
        )
        return candidates


# Singleton
tmdb_service = TMDBService()
