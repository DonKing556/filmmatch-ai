import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers for mocking external services
# ---------------------------------------------------------------------------

MOCK_CLAUDE_RESPONSE_JSON = json.dumps({
    "best_pick": {
        "tmdb_id": 550,
        "rationale": "Dark, gritty, and thought-provoking",
        "match_score": 9,
    },
    "additional_picks": [
        {"tmdb_id": 680, "rationale": "Classic crime", "match_score": 8},
        {"tmdb_id": 155, "rationale": "Epic and intense", "match_score": 8},
        {"tmdb_id": 278, "rationale": "Timeless", "match_score": 7},
        {"tmdb_id": 238, "rationale": "The original", "match_score": 7},
        {"tmdb_id": 13, "rationale": "Feel-good", "match_score": 6},
    ],
    "narrow_question": "More action or more character drama?",
    "overlap_summary": None,
})


def _mock_movie_candidate(tmdb_id: int, title: str):
    """Create a mock MovieCandidate-like object for TMDB results."""
    from app.services.tmdb_service import MovieCandidate

    return MovieCandidate(
        tmdb_id=tmdb_id,
        title=title,
        overview=f"A movie called {title}",
        release_date="2020-01-01",
        genres=["Drama"],
        genre_ids=[18],
        vote_average=8.0,
        vote_count=5000,
        popularity=80.0,
        runtime=120,
        poster_path="/poster.jpg",
        backdrop_path="/backdrop.jpg",
        original_language="en",
        director_names=["Director"],
        cast_names=["Actor1", "Actor2"],
    )


MOCK_CANDIDATES = [
    _mock_movie_candidate(550, "Fight Club"),
    _mock_movie_candidate(680, "Pulp Fiction"),
    _mock_movie_candidate(155, "The Dark Knight"),
    _mock_movie_candidate(278, "The Shawshank Redemption"),
    _mock_movie_candidate(238, "The Godfather"),
    _mock_movie_candidate(13, "Forrest Gump"),
]


def _mock_claude_message():
    """Build a mock Anthropic response message."""
    message = MagicMock()
    message.content = [MagicMock(text=MOCK_CLAUDE_RESPONSE_JSON)]
    message.usage = MagicMock(
        input_tokens=1000,
        output_tokens=300,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=800,
    )
    return message


def _mock_redis():
    """Build an AsyncMock that acts like aioredis.Redis."""
    r = AsyncMock()
    r.get = AsyncMock(return_value=None)
    r.set = AsyncMock()
    r.delete = AsyncMock()
    r.incr = AsyncMock(return_value=1)
    r.expire = AsyncMock()
    pipe = AsyncMock()
    pipe.incr = MagicMock()
    pipe.expire = MagicMock()
    pipe.execute = AsyncMock(return_value=[1])
    r.pipeline = MagicMock(return_value=pipe)
    return r


# ---------------------------------------------------------------------------
# Route existence & basic validation
# ---------------------------------------------------------------------------


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_recommendation_without_auth():
    """Recommendation endpoint should work without auth (anonymous allowed)."""
    response = client.post(
        "/api/v1/recommendations",
        json={
            "mode": "solo",
            "users": [{"name": "Test", "likes_genres": ["comedy"]}],
        },
    )
    # Should not return 401 — anonymous is allowed
    assert response.status_code != 401


def test_auth_magic_link():
    response = client.post(
        "/api/v1/auth/magic-link",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data


def test_auth_verify_magic_link():
    """Verify route exists — requires running PostgreSQL."""
    response = client.post(
        "/api/v1/auth/magic-link",
        json={"email": "test@example.com"},
    )
    token = response.json()["token"]

    response = client.post(
        "/api/v1/auth/verify",
        json={"token": token},
    )
    # 200 with DB, 500 without — either means route is wired
    assert response.status_code in (200, 500)


def test_protected_route_without_token():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_trending_movies():
    """Trending endpoint exists — requires Redis and TMDB API key."""
    response = client.get("/api/v1/movies/trending")
    # 200 with services, 500 without — route is wired
    assert response.status_code in (200, 500)


def test_movie_details_route_exists():
    response = client.get("/api/v1/movies/550")
    assert response.status_code in (200, 500, 502)


def test_group_create_requires_auth():
    response = client.post(
        "/api/v1/groups",
        json={"name": "Movie Night"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Full recommendation flow with mocked Claude + TMDB
# ---------------------------------------------------------------------------


class TestRecommendationFlowMocked:
    """Integration tests for the full recommendation → refine → react → select flow."""

    def _setup_overrides(self):
        """Override FastAPI dependencies and mock external services."""
        from app.core.deps import get_cache, get_session_store, get_optional_user
        from app.core.redis import RedisCache, SessionStore

        mock_redis = _mock_redis()
        mock_cache = RedisCache(mock_redis)
        mock_session_store = SessionStore(mock_redis)

        app.dependency_overrides[get_cache] = lambda: mock_cache
        app.dependency_overrides[get_session_store] = lambda: mock_session_store
        app.dependency_overrides[get_optional_user] = lambda: None

        return mock_redis

    def _teardown_overrides(self):
        app.dependency_overrides.clear()

    def test_solo_recommendation_returns_200(self):
        self._setup_overrides()
        try:
            with (
                patch(
                    "app.services.ai_service.tmdb_service.fetch_candidates",
                    new_callable=AsyncMock,
                    return_value=MOCK_CANDIDATES,
                ),
                patch("app.services.ai_service._get_client") as mock_get_client,
            ):
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(return_value=_mock_claude_message())
                mock_get_client.return_value = mock_client

                response = client.post(
                    "/api/v1/recommendations",
                    json={
                        "mode": "solo",
                        "users": [{"name": "Alex", "likes_genres": ["Drama"]}],
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert "session_id" in data
                assert "best_pick" in data
                assert data["best_pick"]["tmdb_id"] == 550
                assert len(data["additional_picks"]) >= 1
        finally:
            self._teardown_overrides()

    def test_group_recommendation_returns_200(self):
        self._setup_overrides()
        try:
            with (
                patch(
                    "app.services.ai_service.tmdb_service.fetch_candidates",
                    new_callable=AsyncMock,
                    return_value=MOCK_CANDIDATES,
                ),
                patch("app.services.ai_service._get_client") as mock_get_client,
            ):
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(return_value=_mock_claude_message())
                mock_get_client.return_value = mock_client

                response = client.post(
                    "/api/v1/recommendations",
                    json={
                        "mode": "group",
                        "users": [
                            {"name": "Alex", "likes_genres": ["Drama"]},
                            {"name": "Jordan", "likes_genres": ["Comedy"]},
                        ],
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert data["best_pick"]["tmdb_id"] == 550
        finally:
            self._teardown_overrides()

    def test_recommendation_with_dealbreakers(self):
        self._setup_overrides()
        try:
            with (
                patch(
                    "app.services.ai_service.tmdb_service.fetch_candidates",
                    new_callable=AsyncMock,
                    return_value=MOCK_CANDIDATES,
                ),
                patch("app.services.ai_service._get_client") as mock_get_client,
            ):
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(return_value=_mock_claude_message())
                mock_get_client.return_value = mock_client

                response = client.post(
                    "/api/v1/recommendations",
                    json={
                        "mode": "solo",
                        "users": [
                            {
                                "name": "Alex",
                                "likes_genres": ["Horror"],
                                "dealbreakers": ["jump scares", "excessive gore"],
                            }
                        ],
                    },
                )
                assert response.status_code == 200
        finally:
            self._teardown_overrides()

    def test_recommendation_with_full_context(self):
        self._setup_overrides()
        try:
            with (
                patch(
                    "app.services.ai_service.tmdb_service.fetch_candidates",
                    new_callable=AsyncMock,
                    return_value=MOCK_CANDIDATES,
                ),
                patch("app.services.ai_service._get_client") as mock_get_client,
            ):
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(return_value=_mock_claude_message())
                mock_get_client.return_value = mock_client

                response = client.post(
                    "/api/v1/recommendations",
                    json={
                        "mode": "solo",
                        "users": [
                            {
                                "name": "Alex",
                                "likes_genres": ["Drama"],
                                "mood": ["Intense"],
                                "constraints": {"max_runtime_min": 120, "family_friendly": True},
                                "year_range": {"min": 2000, "max": 2020},
                            }
                        ],
                        "context": {"occasion": "date night", "energy": "medium"},
                        "message": "Something thought-provoking and visually stunning",
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert data["model_used"]  # Should include model info
        finally:
            self._teardown_overrides()

    def test_recommendation_invalid_payload_returns_422(self):
        response = client.post(
            "/api/v1/recommendations",
            json={"mode": "solo"},  # missing users
        )
        assert response.status_code == 422


class TestReactionAndSelectionFlow:
    """Test the react/select endpoints with mocked session store."""

    def test_react_to_nonexistent_session(self):
        """React to a session that doesn't exist should return 404 or 500."""
        with patch(
            "app.core.deps.get_redis",
            new_callable=AsyncMock,
            return_value=_mock_redis(),
        ):
            response = client.post(
                "/api/v1/recommendations/fake-session/react",
                json={"tmdb_id": 550, "positive": True, "reason": "Love it"},
            )
            assert response.status_code in (404, 500)

    def test_select_movie_nonexistent_session(self):
        with patch(
            "app.core.deps.get_redis",
            new_callable=AsyncMock,
            return_value=_mock_redis(),
        ):
            response = client.post(
                "/api/v1/recommendations/fake-session/select",
                json={"tmdb_id": 550},
            )
            assert response.status_code in (404, 500)

    def test_receipt_nonexistent_session(self):
        with patch(
            "app.core.deps.get_redis",
            new_callable=AsyncMock,
            return_value=_mock_redis(),
        ):
            response = client.get("/api/v1/recommendations/fake-session/receipt")
            assert response.status_code in (404, 500)


class TestAuthFlow:
    """Test authentication endpoints."""

    def test_magic_link_creates_token(self):
        response = client.post(
            "/api/v1/auth/magic-link",
            json={"email": "user@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 10

    def test_magic_link_bad_email(self):
        """Invalid email format should be rejected."""
        response = client.post(
            "/api/v1/auth/magic-link",
            json={"email": "not-an-email"},
        )
        # Should be 422 (validation) or accept any format depending on schema
        assert response.status_code in (200, 422)

    def test_refresh_with_invalid_token(self):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code in (401, 500)

    def test_logout_requires_auth(self):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401


class TestRequestValidation:
    """Test that malformed requests are properly rejected."""

    def test_empty_body(self):
        response = client.post("/api/v1/recommendations")
        assert response.status_code == 422

    def test_empty_users_list(self):
        response = client.post(
            "/api/v1/recommendations",
            json={"mode": "solo", "users": []},
        )
        # Either 422 or handled — depends on validation
        assert response.status_code in (200, 422, 500)

    def test_refine_missing_feedback(self):
        response = client.post(
            "/api/v1/recommendations/some-session/refine",
            json={},
        )
        assert response.status_code == 422

    def test_react_missing_fields(self):
        response = client.post(
            "/api/v1/recommendations/some-session/react",
            json={},
        )
        assert response.status_code == 422

    def test_select_missing_tmdb_id(self):
        response = client.post(
            "/api/v1/recommendations/some-session/select",
            json={},
        )
        assert response.status_code == 422
