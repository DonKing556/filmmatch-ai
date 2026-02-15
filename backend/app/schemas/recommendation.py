from pydantic import BaseModel


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
    session_id: str
    choice: str
