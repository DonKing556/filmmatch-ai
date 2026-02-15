from pydantic import BaseModel


class PreferencesUpdate(BaseModel):
    preferred_genres: list[int] | None = None
    disliked_genres: list[int] | None = None
    favorite_actors: list[int] | None = None
    favorite_directors: list[int] | None = None
    preferred_decades: list[int] | None = None
    streaming_services: list[str] | None = None
    content_rating_max: str | None = None
    language_preferences: list[str] | None = None


class WatchlistAdd(BaseModel):
    tmdb_id: int
    status: str = "watchlist"


class WatchHistoryItem(BaseModel):
    tmdb_id: int
    title: str | None = None
    poster_url: str | None = None
    status: str
    rating: int | None = None
    created_at: str
