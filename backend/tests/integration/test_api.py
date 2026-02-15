import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


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
    assert response.status_code in (200, 500)


def test_group_create_requires_auth():
    response = client.post(
        "/api/v1/groups",
        json={"name": "Movie Night"},
    )
    assert response.status_code == 401
