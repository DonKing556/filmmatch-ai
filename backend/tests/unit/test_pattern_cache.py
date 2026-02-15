"""Tests for recommendation pattern cache normalization."""

from app.schemas.recommendation import (
    Context,
    RecommendationRequest,
    UserProfile,
    YearRange,
)
from app.services.ai_service import _normalize_cache_key


class TestPatternCacheKey:
    """Test that cache keys are deterministic and normalized."""

    def test_same_request_same_key(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama", "Comedy"])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama", "Comedy"])],
        )
        assert _normalize_cache_key(req1) == _normalize_cache_key(req2)

    def test_genre_order_does_not_matter(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Comedy", "Drama"])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama", "Comedy"])],
        )
        assert _normalize_cache_key(req1) == _normalize_cache_key(req2)

    def test_case_insensitive(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["DRAMA"])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["drama"])],
        )
        assert _normalize_cache_key(req1) == _normalize_cache_key(req2)

    def test_whitespace_trimmed(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["  Drama  "])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama"])],
        )
        assert _normalize_cache_key(req1) == _normalize_cache_key(req2)

    def test_different_genres_different_key(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama"])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Comedy"])],
        )
        assert _normalize_cache_key(req1) != _normalize_cache_key(req2)

    def test_different_modes_different_key(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama"])],
        )
        req2 = RecommendationRequest(
            mode="group",
            users=[UserProfile(name="A", likes_genres=["Drama"])],
        )
        assert _normalize_cache_key(req1) != _normalize_cache_key(req2)

    def test_context_included_in_key(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
            context=Context(occasion="date night"),
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
        )
        assert _normalize_cache_key(req1) != _normalize_cache_key(req2)

    def test_year_range_included(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", year_range=YearRange(min=1990, max=2000))],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
        )
        assert _normalize_cache_key(req1) != _normalize_cache_key(req2)

    def test_key_starts_with_prefix(self):
        req = RecommendationRequest(
            mode="solo", users=[UserProfile(name="A")]
        )
        key = _normalize_cache_key(req)
        assert key.startswith("rec:pattern:")

    def test_key_is_deterministic_length(self):
        req = RecommendationRequest(
            mode="solo", users=[UserProfile(name="A")]
        )
        key = _normalize_cache_key(req)
        # "rec:pattern:" (12) + 16 hex chars = 28
        assert len(key) == 28

    def test_mood_order_normalized(self):
        req1 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", mood=["Intense", "Dark"])],
        )
        req2 = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", mood=["Dark", "Intense"])],
        )
        assert _normalize_cache_key(req1) == _normalize_cache_key(req2)
