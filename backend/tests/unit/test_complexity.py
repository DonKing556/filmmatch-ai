"""Tests for complexity scoring and model routing (Phase 3)."""

from app.schemas.recommendation import (
    Constraints,
    Context,
    RecommendationRequest,
    UserProfile,
)
from app.services.ai_service import compute_complexity, select_model


class TestComplexityScoring:
    """Test the multi-dimensional complexity scoring."""

    def test_solo_minimal_is_simple(self):
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A", likes_genres=["Drama"])],
        )
        result = compute_complexity(req)
        assert result.score == 0
        assert result.tier == "simple"
        assert "haiku" in result.model

    def test_two_users_is_moderate(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A", likes_genres=["Drama"]),
                UserProfile(name="B", likes_genres=["Comedy"]),
            ],
        )
        result = compute_complexity(req)
        assert result.score == 2
        assert result.tier == "simple"  # 2 users = score 2, still simple

    def test_three_users_is_moderate(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A"),
                UserProfile(name="B"),
                UserProfile(name="C"),
            ],
        )
        result = compute_complexity(req)
        assert result.score >= 4  # 3 users = +4
        assert result.tier == "moderate"
        assert "sonnet" in result.model

    def test_five_users_is_complex(self):
        req = RecommendationRequest(
            mode="group",
            users=[UserProfile(name=f"U{i}") for i in range(5)],
        )
        result = compute_complexity(req)
        assert result.score >= 10  # 5 users (+8) + large group (+2) = 10
        assert result.tier == "complex"
        assert "opus" in result.model

    def test_genre_conflicts_increase_score(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A", likes_genres=["Horror", "Thriller"]),
                UserProfile(name="B", dislikes_genres=["Horror"]),
            ],
        )
        result = compute_complexity(req)
        # 2 users (+2), 1 conflict (+1)
        assert result.score >= 3
        assert "genre conflicts" in " ".join(result.reasons).lower() or any(
            "conflict" in r.lower() for r in result.reasons
        )

    def test_constraints_increase_score(self):
        req = RecommendationRequest(
            mode="solo",
            users=[
                UserProfile(
                    name="A",
                    constraints=Constraints(
                        max_runtime_min=120,
                        family_friendly=True,
                    ),
                )
            ],
        )
        result = compute_complexity(req)
        assert result.score >= 2  # 2 constraints

    def test_free_text_increases_score(self):
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
            message="I want something deeply philosophical and thought-provoking like Tarkovsky",
        )
        result = compute_complexity(req)
        assert result.score >= 1

    def test_context_fields_increase_score(self):
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
            context=Context(
                occasion="date night",
                energy="medium",
                familiarity="classic",
            ),
        )
        result = compute_complexity(req)
        assert result.score >= 3  # 3 context fields

    def test_short_message_does_not_increase_score(self):
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="A")],
            message="fun",  # too short
        )
        result = compute_complexity(req)
        assert result.score == 0

    def test_combined_complexity_escalates_to_opus(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(
                    name="A",
                    likes_genres=["Horror"],
                    constraints=Constraints(max_runtime_min=120, family_friendly=True),
                ),
                UserProfile(name="B", dislikes_genres=["Horror"]),
                UserProfile(name="C", likes_genres=["Comedy"]),
            ],
            message="We need something everyone can enjoy but nothing too scary or violent",
            context=Context(occasion="family night", energy="low"),
        )
        result = compute_complexity(req)
        assert result.tier == "complex"
        assert "opus" in result.model


class TestSelectModel:
    """Test the select_model convenience function."""

    def test_returns_string(self):
        req = RecommendationRequest(
            mode="solo", users=[UserProfile(name="A")]
        )
        model = select_model(req)
        assert isinstance(model, str)
        assert "claude" in model

    def test_solo_returns_haiku(self):
        req = RecommendationRequest(
            mode="solo", users=[UserProfile(name="A")]
        )
        assert "haiku" in select_model(req)

    def test_large_group_returns_opus(self):
        req = RecommendationRequest(
            mode="group",
            users=[UserProfile(name=f"U{i}") for i in range(6)],
        )
        assert "opus" in select_model(req)
