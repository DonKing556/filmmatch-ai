"""Tests for taste profile computation (non-DB parts)."""

from app.services.taste_profile import GenreAffinity, TasteProfile


class TestTasteProfilePrompt:
    """Test TasteProfile.to_prompt_context() formatting."""

    def test_empty_profile_returns_empty_string(self):
        profile = TasteProfile(user_id="u1", total_interactions=0)
        assert profile.to_prompt_context() == ""

    def test_liked_genres_appear_in_prompt(self):
        profile = TasteProfile(
            user_id="u1",
            genre_affinities=[
                GenreAffinity(genre="Drama", score=0.8, interactions=10),
                GenreAffinity(genre="Comedy", score=0.5, interactions=5),
            ],
            total_interactions=15,
        )
        ctx = profile.to_prompt_context()
        assert "Drama" in ctx
        assert "Comedy" in ctx
        assert "Implicit genre preferences" in ctx

    def test_disliked_genres_appear_in_prompt(self):
        profile = TasteProfile(
            user_id="u1",
            genre_affinities=[
                GenreAffinity(genre="Horror", score=-0.6, interactions=8),
            ],
            total_interactions=8,
        )
        ctx = profile.to_prompt_context()
        assert "Horror" in ctx
        assert "avoid" in ctx.lower()

    def test_weak_affinities_excluded(self):
        """Genres with score between -0.2 and 0.2 should not appear."""
        profile = TasteProfile(
            user_id="u1",
            genre_affinities=[
                GenreAffinity(genre="Documentary", score=0.1, interactions=3),
            ],
            total_interactions=3,
        )
        ctx = profile.to_prompt_context()
        assert "Documentary" not in ctx

    def test_directors_and_actors_in_prompt(self):
        profile = TasteProfile(
            user_id="u1",
            top_directors=["Nolan", "Villeneuve"],
            top_actors=["Gosling", "Blunt"],
            total_interactions=20,
        )
        ctx = profile.to_prompt_context()
        assert "Nolan" in ctx
        assert "Gosling" in ctx

    def test_preferred_decades_in_prompt(self):
        profile = TasteProfile(
            user_id="u1",
            preferred_decades=["1990s", "2000s"],
            total_interactions=10,
        )
        ctx = profile.to_prompt_context()
        assert "1990s" in ctx

    def test_max_five_liked_genres(self):
        affinities = [
            GenreAffinity(genre=f"Genre{i}", score=0.9 - i * 0.05, interactions=5)
            for i in range(8)
        ]
        profile = TasteProfile(
            user_id="u1", genre_affinities=affinities, total_interactions=40
        )
        ctx = profile.to_prompt_context()
        # At most 5 liked genres should appear in the preferences line
        pref_line = [l for l in ctx.split("\n") if "Implicit genre" in l][0]
        assert pref_line.count("Genre") <= 5


class TestTasteProfileDict:
    """Test TasteProfile.to_dict() serialization."""

    def test_round_trip_fields(self):
        profile = TasteProfile(
            user_id="u1",
            genre_affinities=[
                GenreAffinity(genre="Action", score=0.756, interactions=12),
            ],
            preferred_decades=["2010s"],
            top_directors=["Nolan"],
            top_actors=["Hardy"],
            avg_rating=7.345,
            total_interactions=30,
        )
        d = profile.to_dict()
        assert d["user_id"] == "u1"
        assert d["total_interactions"] == 30
        assert d["avg_rating"] == 7.3  # rounded to 1 decimal
        assert d["genre_affinities"][0]["score"] == 0.76  # rounded to 2 decimals
        assert d["genre_affinities"][0]["genre"] == "Action"
        assert d["preferred_decades"] == ["2010s"]

    def test_none_avg_rating(self):
        profile = TasteProfile(user_id="u1")
        d = profile.to_dict()
        assert d["avg_rating"] is None
