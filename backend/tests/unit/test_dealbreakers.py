"""Tests for the dealbreaker ('Save me from...') feature."""

from app.schemas.recommendation import RecommendationRequest, UserProfile
from app.services.ai_service import _build_candidate_prompt
from app.services.tmdb_service import MovieCandidate


def _mc(tmdb_id: int, title: str) -> MovieCandidate:
    return MovieCandidate(
        tmdb_id=tmdb_id,
        title=title,
        overview=f"A movie called {title}",
        release_date="2020-01-01",
        genres=["Drama"],
        genre_ids=[18],
        vote_average=7.0,
        vote_count=1000,
        popularity=50.0,
        runtime=120,
        poster_path="/test.jpg",
        backdrop_path="/backdrop.jpg",
        original_language="en",
        director_names=["Director"],
        cast_names=["Actor"],
    )


class TestDealbreakers:
    def test_schema_accepts_dealbreakers(self):
        profile = UserProfile(
            name="Alex",
            likes_genres=["Drama"],
            dealbreakers=["jump scares", "slow pacing"],
        )
        assert len(profile.dealbreakers) == 2
        assert "jump scares" in profile.dealbreakers

    def test_schema_defaults_empty_dealbreakers(self):
        profile = UserProfile(name="Alex")
        assert profile.dealbreakers == []

    def test_prompt_includes_dealbreakers(self):
        req = RecommendationRequest(
            mode="solo",
            users=[
                UserProfile(
                    name="Alex",
                    likes_genres=["Horror"],
                    dealbreakers=["jump scares", "excessive violence"],
                )
            ],
        )
        candidates = [_mc(1, "Test Movie")]
        prompt = _build_candidate_prompt(candidates, req)
        assert "DEALBREAKERS" in prompt
        assert "jump scares" in prompt
        assert "excessive violence" in prompt

    def test_prompt_omits_dealbreaker_section_when_empty(self):
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="Alex", likes_genres=["Drama"])],
        )
        candidates = [_mc(1, "Test Movie")]
        prompt = _build_candidate_prompt(candidates, req)
        assert "DEALBREAKERS" not in prompt

    def test_group_dealbreakers_merged_in_prompt(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A", dealbreakers=["sad endings"]),
                UserProfile(name="B", dealbreakers=["excessive violence"]),
            ],
        )
        candidates = [_mc(1, "Test Movie")]
        prompt = _build_candidate_prompt(candidates, req)
        assert "sad endings" in prompt
        assert "excessive violence" in prompt
