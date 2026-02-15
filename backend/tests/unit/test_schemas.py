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


# ---------- Extended schema tests (Phase 4) ----------

import pytest
from pydantic import ValidationError
from app.schemas.recommendation import (
    Constraints,
    Context,
    ReactionRequest,
    SelectionRequest,
    YearRange,
)


class TestUserProfileExtended:
    def test_defaults_are_empty(self):
        p = UserProfile(name="A")
        assert p.likes_genres == []
        assert p.dislikes_genres == []
        assert p.dealbreakers == []
        assert p.mood == []
        assert p.constraints is None
        assert p.year_range is None

    def test_full_profile(self):
        p = UserProfile(
            name="B",
            likes_genres=["Action", "Sci-Fi"],
            dislikes_genres=["Romance"],
            dealbreakers=["jump scares"],
            favorite_actors=["Keanu"],
            favorite_directors=["Wachowski"],
            year_range=YearRange(min=2000, max=2020),
            mood=["Intense"],
            constraints=Constraints(max_runtime_min=150, family_friendly=True),
        )
        assert len(p.likes_genres) == 2
        assert p.constraints.max_runtime_min == 150
        assert p.year_range.min == 2000

    def test_name_required(self):
        with pytest.raises(ValidationError):
            UserProfile()


class TestConstraintsSchema:
    def test_all_optional(self):
        c = Constraints()
        assert c.max_runtime_min is None
        assert c.subtitles_ok is None
        assert c.streaming_services is None
        assert c.family_friendly is None

    def test_streaming_services(self):
        c = Constraints(streaming_services=["Netflix", "Hulu"])
        assert len(c.streaming_services) == 2


class TestContextSchema:
    def test_defaults(self):
        ctx = Context()
        assert ctx.occasion is None
        assert ctx.energy is None
        assert ctx.want_something_new is False

    def test_set_fields(self):
        ctx = Context(occasion="date night", energy="low", familiarity="classic")
        assert ctx.occasion == "date night"


class TestRecommendationRequestExtended:
    def test_users_required(self):
        with pytest.raises(ValidationError):
            RecommendationRequest(mode="solo")

    def test_mode_defaults_to_solo(self):
        req = RecommendationRequest(users=[UserProfile(name="A")])
        assert req.mode == "solo"

    def test_with_message_and_context(self):
        req = RecommendationRequest(
            mode="group",
            users=[UserProfile(name="A"), UserProfile(name="B")],
            context=Context(occasion="movie night"),
            message="Something fun",
        )
        assert req.message == "Something fun"
        assert req.context.occasion == "movie night"


class TestReactionRequestSchema:
    def test_minimal(self):
        r = ReactionRequest(tmdb_id=550, positive=True)
        assert r.reason is None

    def test_with_reason(self):
        r = ReactionRequest(tmdb_id=550, positive=False, reason="too long")
        assert r.reason == "too long"


class TestSelectionRequestSchema:
    def test_basic(self):
        s = SelectionRequest(tmdb_id=550)
        assert s.tmdb_id == 550


class TestMovieSummaryExtended:
    def test_defaults(self):
        m = MovieSummary(tmdb_id=1, title="Test")
        assert m.year is None
        assert m.genres == []
        assert m.vote_average == 0
        assert m.rationale == ""
        assert m.match_score is None

    def test_full(self):
        m = MovieSummary(
            tmdb_id=550,
            title="Fight Club",
            year="1999",
            genres=["Drama"],
            vote_average=8.4,
            runtime=139,
            match_score=0.92,
            rationale="Dark and gritty.",
        )
        assert m.match_score == 0.92


class TestRecommendationResponseExtended:
    def test_defaults(self):
        resp = RecommendationResponse(
            session_id="abc",
            best_pick=MovieSummary(tmdb_id=1, title="Movie"),
        )
        assert resp.additional_picks == []
        assert resp.narrow_question is None
        assert resp.model_used == ""
        assert resp.overlap_summary is None
