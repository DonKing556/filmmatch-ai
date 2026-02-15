import json

from app.schemas.recommendation import RecommendationRequest, UserProfile
from app.services.ai_service import (
    _build_candidate_prompt,
    _candidate_to_summary,
    _parse_ai_response,
    select_model,
)
from app.services.tmdb_service import MovieCandidate


def _make_candidate(tmdb_id: int, title: str, vote_avg: float = 7.0) -> MovieCandidate:
    return MovieCandidate(
        tmdb_id=tmdb_id,
        title=title,
        overview=f"A movie called {title}",
        release_date="2020-01-01",
        genres=["Drama"],
        genre_ids=[18],
        vote_average=vote_avg,
        vote_count=1000,
        popularity=50.0,
        runtime=120,
        poster_path="/test.jpg",
        backdrop_path="/backdrop.jpg",
        original_language="en",
        director_names=["Test Director"],
        cast_names=["Actor A", "Actor B"],
    )


def test_select_model_solo():
    req = RecommendationRequest(
        mode="solo",
        users=[UserProfile(name="Mike")],
    )
    model = select_model(req)
    assert "haiku" in model


def test_select_model_group():
    # 2 users = score 2, still "simple" tier → Haiku
    # Need 3+ users to hit "moderate" tier → Sonnet
    req = RecommendationRequest(
        mode="group",
        users=[UserProfile(name="Mike"), UserProfile(name="Sarah")],
    )
    model = select_model(req)
    assert "haiku" in model


def test_build_candidate_prompt():
    candidates = [_make_candidate(550, "Fight Club"), _make_candidate(680, "Pulp Fiction")]
    req = RecommendationRequest(
        mode="solo",
        users=[UserProfile(name="Mike", likes_genres=["drama"])],
    )
    prompt = _build_candidate_prompt(candidates, req)
    assert "TMDB ID: 550" in prompt
    assert "TMDB ID: 680" in prompt
    assert "MUST ONLY recommend movies from the numbered list" in prompt


def test_candidate_to_summary():
    candidate = _make_candidate(550, "Fight Club", 8.4)
    summary = _candidate_to_summary(candidate, match_score=9.0, rationale="Great pick")
    assert summary.tmdb_id == 550
    assert summary.title == "Fight Club"
    assert summary.match_score == 9.0
    assert summary.rationale == "Great pick"
    assert summary.poster_url is not None


def test_parse_valid_ai_response():
    candidates = [
        _make_candidate(550, "Fight Club", 8.4),
        _make_candidate(680, "Pulp Fiction", 8.9),
        _make_candidate(13, "Forrest Gump", 8.5),
        _make_candidate(155, "The Dark Knight", 9.0),
        _make_candidate(278, "Shawshank", 9.3),
        _make_candidate(238, "The Godfather", 8.7),
    ]
    ai_response = json.dumps({
        "best_pick": {
            "tmdb_id": 550,
            "rationale": "Gritty and smart",
            "match_score": 9,
        },
        "additional_picks": [
            {"tmdb_id": 680, "rationale": "Classic crime", "match_score": 8},
            {"tmdb_id": 155, "rationale": "Dark and intense", "match_score": 8},
            {"tmdb_id": 278, "rationale": "Timeless", "match_score": 7},
            {"tmdb_id": 238, "rationale": "The original", "match_score": 7},
            {"tmdb_id": 13, "rationale": "Feel-good", "match_score": 6},
        ],
        "narrow_question": "More funny or more tense?",
    })

    result = _parse_ai_response(ai_response, candidates, "sess-1", "haiku")
    assert result.best_pick.tmdb_id == 550
    assert len(result.additional_picks) == 5
    assert result.narrow_question == "More funny or more tense?"


def test_parse_ai_response_with_hallucinated_id():
    candidates = [
        _make_candidate(550, "Fight Club", 8.4),
        _make_candidate(680, "Pulp Fiction", 8.9),
        _make_candidate(13, "Forrest Gump", 8.5),
        _make_candidate(155, "The Dark Knight", 9.0),
        _make_candidate(278, "Shawshank", 9.3),
        _make_candidate(238, "The Godfather", 8.7),
    ]
    ai_response = json.dumps({
        "best_pick": {
            "tmdb_id": 99999,  # Hallucinated
            "rationale": "Made up movie",
            "match_score": 10,
        },
        "additional_picks": [
            {"tmdb_id": 680, "rationale": "Real", "match_score": 8},
        ],
        "narrow_question": "More?",
    })

    result = _parse_ai_response(ai_response, candidates, "sess-1", "haiku")
    # Should fall back to first candidate
    assert result.best_pick.tmdb_id == 550
    # Should backfill to 5 additional picks
    assert len(result.additional_picks) == 5


def test_parse_invalid_json_fallback():
    candidates = [
        _make_candidate(550, "Fight Club", 8.4),
        _make_candidate(680, "Pulp Fiction", 8.9),
        _make_candidate(13, "Forrest Gump", 8.5),
        _make_candidate(155, "The Dark Knight", 9.0),
        _make_candidate(278, "Shawshank", 9.3),
        _make_candidate(238, "The Godfather", 8.7),
    ]

    result = _parse_ai_response("This is not JSON at all!", candidates, "sess-1", "haiku")
    # Should fallback to vote_average ranking
    assert result.best_pick.tmdb_id == 278  # Shawshank has highest vote_average
    assert len(result.additional_picks) == 5
