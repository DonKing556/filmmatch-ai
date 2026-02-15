"""Quality evaluation pipeline for recommendation outputs.

Measures:
  - Hallucination rate: picks must exist in the candidate set
  - Constraint adherence: picks respect runtime, genre, year constraints
  - Genre relevance: picks should overlap with requested genres
  - Diversity: picks should cover multiple genres
  - Score quality: match scores should be reasonable
  - Response structure: JSON format compliance

Run against golden test cases using pre-validated _parse_ai_response output
(no actual Claude call needed — we test the parse/validate layer).
"""

import json
from dataclasses import dataclass, field

import pytest

from app.services.ai_service import _build_candidate_prompt, _parse_ai_response, compute_complexity
from app.schemas.recommendation import (
    Context,
    RecommendationRequest,
    RecommendationResponse,
    UserProfile,
)
from app.services.tmdb_service import MovieCandidate
from tests.quality.golden_cases import GOLDEN_CASES, GoldenCase


# ---------------------------------------------------------------------------
# Quality metrics
# ---------------------------------------------------------------------------

@dataclass
class QualityMetrics:
    case_name: str
    hallucination_count: int = 0
    total_picks: int = 0
    genre_hits: int = 0
    genre_checks: int = 0
    forbidden_genre_violations: int = 0
    runtime_violations: int = 0
    diversity_score: int = 0  # number of distinct genres across all picks
    best_match_score: float = 0.0
    all_scores_reasonable: bool = True
    passed: bool = True
    failures: list[str] = field(default_factory=list)


def evaluate_response(
    case: GoldenCase,
    response: RecommendationResponse,
    candidate_map: dict[int, MovieCandidate],
) -> QualityMetrics:
    """Evaluate a recommendation response against a golden case."""
    metrics = QualityMetrics(case_name=case.name)

    all_picks = [response.best_pick] + response.additional_picks
    metrics.total_picks = len(all_picks)

    all_genres_seen: set[str] = set()

    for pick in all_picks:
        # Hallucination check
        if pick.tmdb_id not in candidate_map:
            metrics.hallucination_count += 1
            metrics.failures.append(f"Hallucinated TMDB ID: {pick.tmdb_id}")

        candidate = candidate_map.get(pick.tmdb_id)
        if candidate is None:
            continue

        # Genre relevance
        if case.expected_genre_overlap:
            for expected_genre in case.expected_genre_overlap:
                metrics.genre_checks += 1
                if expected_genre in candidate.genres:
                    metrics.genre_hits += 1

        # Forbidden genre check
        for fg in case.forbidden_genres:
            if fg in candidate.genres:
                metrics.forbidden_genre_violations += 1
                metrics.failures.append(
                    f"{candidate.title} contains forbidden genre: {fg}"
                )

        # Runtime check
        if case.max_runtime and candidate.runtime and candidate.runtime > case.max_runtime:
            metrics.runtime_violations += 1
            metrics.failures.append(
                f"{candidate.title} runtime {candidate.runtime} > max {case.max_runtime}"
            )

        # Track diversity
        all_genres_seen.update(candidate.genres)

        # Score reasonableness (1-10 range)
        if pick.match_score is not None:
            if not (1 <= pick.match_score <= 10):
                metrics.all_scores_reasonable = False
                metrics.failures.append(
                    f"{candidate.title} score {pick.match_score} out of 1-10 range"
                )

    metrics.diversity_score = len(all_genres_seen)

    if response.best_pick.match_score is not None:
        metrics.best_match_score = response.best_pick.match_score

    # Determine pass/fail
    metrics.passed = (
        metrics.hallucination_count == 0
        and metrics.forbidden_genre_violations == 0
        and metrics.all_scores_reasonable
    )

    return metrics


# ---------------------------------------------------------------------------
# Pytest-based evaluation (runs without Claude — tests parse layer)
# ---------------------------------------------------------------------------

def _make_perfect_ai_response(
    case: GoldenCase,
) -> str:
    """Generate a synthetic 'perfect' AI response from the candidate pool.

    Picks the best candidates that align with the case expectations.
    Used to test the _parse_ai_response layer itself.
    """
    candidate_map = {c.tmdb_id: c for c in case.candidates}

    # Score candidates by alignment with request
    scored = []
    liked_genres = set()
    disliked_genres = set()
    for user in case.request.users:
        liked_genres.update(g.lower() for g in user.likes_genres)
        disliked_genres.update(g.lower() for g in user.dislikes_genres)

    for c in case.candidates:
        score = 0
        c_genres = {g.lower() for g in c.genres}
        score += len(c_genres & liked_genres) * 3
        score -= len(c_genres & disliked_genres) * 5
        score += c.vote_average
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    best = scored[0][1]
    additional = [s[1] for s in scored[1:6]]

    data = {
        "best_pick": {
            "tmdb_id": best.tmdb_id,
            "rationale": f"Great match for your preferences",
            "match_score": min(10, round(scored[0][0] / 3, 1)),
        },
        "additional_picks": [
            {
                "tmdb_id": c.tmdb_id,
                "rationale": f"Solid pick",
                "match_score": min(10, round(s / 3, 1)),
            }
            for s, c in scored[1:6]
        ],
        "narrow_question": "Would you prefer something lighter or darker?",
    }

    if case.request.mode == "group":
        data["overlap_summary"] = "The group shares an interest in compelling storytelling."

    return json.dumps(data)


class TestComplexityScoring:
    """Test the complexity scoring and model routing."""

    def test_solo_simple_routes_to_haiku(self):
        req = RecommendationRequest(
            mode="solo", users=[UserProfile(name="A")]
        )
        result = compute_complexity(req)
        assert result.tier == "simple"
        assert "haiku" in result.model

    def test_two_users_stays_simple(self):
        # 2 users = score 2, still "simple" tier (Haiku)
        req = RecommendationRequest(
            mode="group",
            users=[UserProfile(name="A"), UserProfile(name="B")],
        )
        result = compute_complexity(req)
        assert result.score == 2
        assert result.tier == "simple"
        assert "haiku" in result.model

    def test_large_group_routes_to_opus(self):
        req = RecommendationRequest(
            mode="group",
            users=[UserProfile(name=f"U{i}") for i in range(5)],
        )
        result = compute_complexity(req)
        assert result.tier == "complex"
        assert "opus" in result.model

    def test_solo_with_many_constraints_escalates(self):
        from app.schemas.recommendation import Constraints
        req = RecommendationRequest(
            mode="solo",
            users=[UserProfile(
                name="A",
                constraints=Constraints(
                    max_runtime_min=120,
                    family_friendly=True,
                    streaming_services=["netflix"],
                    subtitles_ok=False,
                ),
            )],
            message="I want something deeply philosophical and thought-provoking",
            context=Context(occasion="solo night", energy="low", familiarity="classic"),
        )
        result = compute_complexity(req)
        assert result.score >= 6
        assert result.tier == "complex"

    def test_genre_conflicts_increase_score(self):
        req = RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A", likes_genres=["Horror"]),
                UserProfile(name="B", dislikes_genres=["Horror"]),
            ],
        )
        result = compute_complexity(req)
        # 2 users (+2) + 1 conflict (+1) = 3 -> moderate
        assert result.score >= 3


class TestResponseParsing:
    """Test that _parse_ai_response correctly validates against candidates."""

    @pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c.name for c in GOLDEN_CASES])
    def test_golden_case_structure(self, case: GoldenCase):
        """Ensure parsed responses have correct structure for all golden cases."""
        ai_text = _make_perfect_ai_response(case)
        result = _parse_ai_response(
            ai_text, case.candidates, "test-session", "test-model"
        )
        assert result.best_pick is not None
        assert result.best_pick.tmdb_id in {c.tmdb_id for c in case.candidates}
        assert len(result.additional_picks) >= 1

    @pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c.name for c in GOLDEN_CASES])
    def test_no_hallucinations(self, case: GoldenCase):
        """No pick should have a TMDB ID not in the candidate set."""
        ai_text = _make_perfect_ai_response(case)
        result = _parse_ai_response(
            ai_text, case.candidates, "test-session", "test-model"
        )
        candidate_ids = {c.tmdb_id for c in case.candidates}
        all_pick_ids = [result.best_pick.tmdb_id] + [
            p.tmdb_id for p in result.additional_picks
        ]
        for pid in all_pick_ids:
            assert pid in candidate_ids, f"Hallucinated TMDB ID: {pid}"

    @pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c.name for c in GOLDEN_CASES])
    def test_quality_metrics(self, case: GoldenCase):
        """Run full quality evaluation on each golden case."""
        ai_text = _make_perfect_ai_response(case)
        result = _parse_ai_response(
            ai_text, case.candidates, "test-session", "test-model"
        )
        candidate_map = {c.tmdb_id: c for c in case.candidates}
        metrics = evaluate_response(case, result, candidate_map)

        assert metrics.hallucination_count == 0, (
            f"Hallucinations: {metrics.failures}"
        )
        assert metrics.all_scores_reasonable, (
            f"Score issues: {metrics.failures}"
        )


class TestPromptBuilding:
    """Test that prompts are well-formed for golden cases."""

    @pytest.mark.parametrize("case", GOLDEN_CASES[:5], ids=[c.name for c in GOLDEN_CASES[:5]])
    def test_prompt_contains_all_candidates(self, case: GoldenCase):
        prompt = _build_candidate_prompt(case.candidates, case.request)
        for c in case.candidates:
            assert str(c.tmdb_id) in prompt

    def test_prompt_contains_rules(self):
        case = GOLDEN_CASES[0]
        prompt = _build_candidate_prompt(case.candidates, case.request)
        assert "MUST ONLY recommend movies from the numbered list" in prompt
        assert "Do NOT recommend any movie not in this list" in prompt
