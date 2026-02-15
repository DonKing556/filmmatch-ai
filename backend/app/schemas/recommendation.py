from pydantic import BaseModel, Field


class YearRange(BaseModel):
    min: int | None = None
    max: int | None = None


class Constraints(BaseModel):
    max_runtime_min: int | None = None
    subtitles_ok: bool | None = None
    streaming_services: list[str] | None = None
    family_friendly: bool | None = None


class UserProfile(BaseModel):
    name: str
    likes_genres: list[str] = []
    dislikes_genres: list[str] = []
    favorite_actors: list[str] = []
    favorite_directors: list[str] = []
    year_range: YearRange | None = None
    mood: list[str] = []
    constraints: Constraints | None = None


class Context(BaseModel):
    occasion: str | None = None
    energy: str | None = None
    want_something_new: bool = False
    familiarity: str | None = None


class RecommendationRequest(BaseModel):
    mode: str = "solo"
    users: list[UserProfile]
    context: Context | None = None
    message: str | None = None


class NarrowRequest(BaseModel):
    feedback: str
    keep_tmdb_ids: list[int] = []
    reject_tmdb_ids: list[int] = []


class ReactionRequest(BaseModel):
    tmdb_id: int
    positive: bool
    reason: str | None = None


class SelectionRequest(BaseModel):
    tmdb_id: int


class MovieSummary(BaseModel):
    tmdb_id: int
    title: str
    year: str | None = None
    genres: list[str] = []
    vote_average: float = 0
    runtime: int | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    overview: str = ""
    directors: list[str] = []
    cast: list[str] = []
    match_score: float | None = None
    rationale: str = ""


class RecommendationResponse(BaseModel):
    session_id: str
    best_pick: MovieSummary
    additional_picks: list[MovieSummary] = []
    narrow_question: str | None = None
    overlap_summary: str | None = None
    model_used: str = ""


class StreamStatus(BaseModel):
    event: str
    data: str
