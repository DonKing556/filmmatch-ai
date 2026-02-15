from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    MovieSummary,
    NarrowRequest,
    UserProfile,
)
from app.schemas.auth import MagicLinkRequest, TokenResponse
from app.schemas.group import GroupCreate, GroupJoin


def test_solo_request_minimal():
    req = RecommendationRequest(
        mode="solo",
        users=[UserProfile(name="Mike", likes_genres=["thriller"])],
    )
    assert req.mode == "solo"
    assert len(req.users) == 1
    assert req.users[0].likes_genres == ["thriller"]


def test_group_request():
    req = RecommendationRequest(
        mode="group",
        users=[
            UserProfile(name="Mike", likes_genres=["crime"]),
            UserProfile(name="Sarah", likes_genres=["comedy"]),
        ],
    )
    assert req.mode == "group"
    assert len(req.users) == 2


def test_movie_summary():
    movie = MovieSummary(
        tmdb_id=550,
        title="Fight Club",
        year="1999",
        genres=["Drama", "Thriller"],
        vote_average=8.4,
        runtime=139,
        rationale="Gritty and smart",
    )
    assert movie.tmdb_id == 550
    assert movie.vote_average == 8.4


def test_recommendation_response():
    resp = RecommendationResponse(
        session_id="abc-123",
        best_pick=MovieSummary(tmdb_id=550, title="Fight Club"),
        additional_picks=[
            MovieSummary(tmdb_id=680, title="Pulp Fiction"),
        ],
        narrow_question="More action or more drama?",
        model_used="claude-haiku-4-5-20250514",
    )
    assert resp.session_id == "abc-123"
    assert len(resp.additional_picks) == 1


def test_narrow_request():
    req = NarrowRequest(
        feedback="Something more lighthearted",
        keep_tmdb_ids=[550],
        reject_tmdb_ids=[680],
    )
    assert req.feedback == "Something more lighthearted"
    assert 550 in req.keep_tmdb_ids


def test_magic_link_request():
    req = MagicLinkRequest(email="test@example.com")
    assert req.email == "test@example.com"


def test_group_create():
    req = GroupCreate(name="Movie Night")
    assert req.name == "Movie Night"


def test_group_join():
    req = GroupJoin(join_code="ABC123")
    assert req.join_code == "ABC123"
