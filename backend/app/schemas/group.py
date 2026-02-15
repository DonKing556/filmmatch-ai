from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str | None = None


class GroupJoin(BaseModel):
    join_code: str


class GroupMemberPreferences(BaseModel):
    likes_genres: list[str] = []
    dislikes_genres: list[str] = []
    mood: list[str] = []
    constraints: dict | None = None


class GroupResponse(BaseModel):
    id: str
    name: str | None = None
    join_code: str
    member_count: int
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True
