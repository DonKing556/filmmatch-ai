"""Golden test cases for recommendation quality evaluation.

Each case defines a request scenario, a set of candidate movies, and
expectations about what a quality response should contain.
"""

from app.schemas.recommendation import (
    Context,
    Constraints,
    RecommendationRequest,
    UserProfile,
    YearRange,
)
from app.services.tmdb_service import MovieCandidate


def _mc(
    tmdb_id: int,
    title: str,
    genres: list[str],
    genre_ids: list[int],
    vote_avg: float = 7.0,
    runtime: int = 120,
    year: str = "2020-01-01",
    language: str = "en",
    directors: list[str] | None = None,
    cast: list[str] | None = None,
) -> MovieCandidate:
    return MovieCandidate(
        tmdb_id=tmdb_id,
        title=title,
        overview=f"A movie called {title}",
        release_date=year,
        genres=genres,
        genre_ids=genre_ids,
        vote_average=vote_avg,
        vote_count=1000,
        popularity=50.0,
        runtime=runtime,
        poster_path="/test.jpg",
        backdrop_path="/backdrop.jpg",
        original_language=language,
        director_names=directors or ["Director"],
        cast_names=cast or ["Actor A", "Actor B"],
    )


# ---------------------------------------------------------------------------
# Candidate pool (shared across test cases)
# ---------------------------------------------------------------------------

CANDIDATE_POOL = [
    _mc(550, "Fight Club", ["Drama", "Thriller"], [18, 53], 8.4, 139, "1999-10-15",
        directors=["David Fincher"], cast=["Brad Pitt", "Edward Norton"]),
    _mc(680, "Pulp Fiction", ["Crime", "Thriller"], [80, 53], 8.9, 154, "1994-09-10",
        directors=["Quentin Tarantino"], cast=["John Travolta", "Samuel L. Jackson"]),
    _mc(13, "Forrest Gump", ["Comedy", "Drama", "Romance"], [35, 18, 10749], 8.5, 142, "1994-07-06",
        directors=["Robert Zemeckis"], cast=["Tom Hanks", "Robin Wright"]),
    _mc(155, "The Dark Knight", ["Action", "Crime", "Drama"], [28, 80, 18], 9.0, 152, "2008-07-16",
        directors=["Christopher Nolan"], cast=["Christian Bale", "Heath Ledger"]),
    _mc(278, "The Shawshank Redemption", ["Drama", "Crime"], [18, 80], 9.3, 142, "1994-09-23",
        directors=["Frank Darabont"], cast=["Tim Robbins", "Morgan Freeman"]),
    _mc(238, "The Godfather", ["Drama", "Crime"], [18, 80], 8.7, 175, "1972-03-14",
        directors=["Francis Ford Coppola"], cast=["Marlon Brando", "Al Pacino"]),
    _mc(603, "The Matrix", ["Action", "Science Fiction"], [28, 878], 8.2, 136, "1999-03-30",
        directors=["Lana Wachowski", "Lilly Wachowski"], cast=["Keanu Reeves", "Laurence Fishburne"]),
    _mc(120, "The Lord of the Rings: Fellowship", ["Adventure", "Fantasy", "Action"], [12, 14, 28], 8.4, 178, "2001-12-18",
        directors=["Peter Jackson"], cast=["Elijah Wood", "Ian McKellen"]),
    _mc(27205, "Inception", ["Action", "Science Fiction", "Adventure"], [28, 878, 12], 8.4, 148, "2010-07-15",
        directors=["Christopher Nolan"], cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"]),
    _mc(424, "Schindler's List", ["Drama", "History", "War"], [18, 36, 10752], 8.6, 195, "1993-11-30",
        directors=["Steven Spielberg"], cast=["Liam Neeson", "Ralph Fiennes"]),
    _mc(11, "Star Wars", ["Adventure", "Action", "Science Fiction"], [12, 28, 878], 8.2, 121, "1977-05-25",
        directors=["George Lucas"], cast=["Mark Hamill", "Harrison Ford"]),
    _mc(497, "The Green Mile", ["Fantasy", "Drama", "Crime"], [14, 18, 80], 8.5, 189, "1999-12-10",
        directors=["Frank Darabont"], cast=["Tom Hanks", "Michael Clarke Duncan"]),
    _mc(769, "GoodFellas", ["Crime", "Drama"], [80, 18], 8.5, 146, "1990-09-12",
        directors=["Martin Scorsese"], cast=["Robert De Niro", "Ray Liotta"]),
    _mc(105, "Back to the Future", ["Comedy", "Adventure", "Science Fiction"], [35, 12, 878], 8.3, 116, "1985-07-03",
        directors=["Robert Zemeckis"], cast=["Michael J. Fox", "Christopher Lloyd"]),
    _mc(807, "Se7en", ["Crime", "Mystery", "Thriller"], [80, 9648, 53], 8.4, 127, "1995-09-22",
        directors=["David Fincher"], cast=["Brad Pitt", "Morgan Freeman"]),
    _mc(539, "Psycho", ["Horror", "Thriller"], [27, 53], 8.4, 109, "1960-06-16",
        directors=["Alfred Hitchcock"], cast=["Anthony Perkins", "Janet Leigh"]),
    _mc(862, "Toy Story", ["Animation", "Comedy", "Family"], [16, 35, 10751], 8.0, 81, "1995-10-30",
        directors=["John Lasseter"], cast=["Tom Hanks", "Tim Allen"]),
    _mc(597, "Titanic", ["Drama", "Romance"], [18, 10749], 7.9, 194, "1997-11-18",
        directors=["James Cameron"], cast=["Leonardo DiCaprio", "Kate Winslet"]),
    _mc(274, "The Silence of the Lambs", ["Crime", "Drama", "Thriller"], [80, 18, 53], 8.4, 118, "1991-02-01",
        directors=["Jonathan Demme"], cast=["Jodie Foster", "Anthony Hopkins"]),
    _mc(429, "The Good, the Bad and the Ugly", ["Western"], [37], 8.5, 161, "1966-12-23",
        directors=["Sergio Leone"], cast=["Clint Eastwood", "Eli Wallach"]),
]


# ---------------------------------------------------------------------------
# Golden test case definitions
# ---------------------------------------------------------------------------

class GoldenCase:
    def __init__(
        self,
        name: str,
        request: RecommendationRequest,
        candidates: list[MovieCandidate],
        expected_genre_overlap: list[str] | None = None,
        forbidden_genres: list[str] | None = None,
        max_runtime: int | None = None,
        expected_diversity_min: int = 2,
        expected_best_score_min: float = 6.0,
    ):
        self.name = name
        self.request = request
        self.candidates = candidates
        self.expected_genre_overlap = expected_genre_overlap or []
        self.forbidden_genres = forbidden_genres or []
        self.max_runtime = max_runtime
        self.expected_diversity_min = expected_diversity_min
        self.expected_best_score_min = expected_best_score_min


GOLDEN_CASES: list[GoldenCase] = [
    # 1. Solo drama lover
    GoldenCase(
        name="solo_drama_lover",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="Alex", likes_genres=["Drama"], mood=["Emotional"])],
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Drama"],
        expected_best_score_min=7.0,
    ),
    # 2. Solo action fan, hates romance
    GoldenCase(
        name="solo_action_no_romance",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(
                name="Jake",
                likes_genres=["Action", "Sci-Fi"],
                dislikes_genres=["Romance"],
                mood=["Intense"],
            )],
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Action"],
        forbidden_genres=["Romance"],
        expected_best_score_min=7.0,
    ),
    # 3. Family night — short runtime
    GoldenCase(
        name="family_night_short",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(
                name="Family",
                likes_genres=["Comedy", "Animation", "Family"],
                dislikes_genres=["Horror", "Crime"],
                constraints=Constraints(max_runtime_min=120, family_friendly=True),
            )],
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Comedy"],
        forbidden_genres=["Horror", "Crime"],
        max_runtime=120,
    ),
    # 4. Group of 2 with overlapping tastes
    GoldenCase(
        name="group_2_overlap",
        request=RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="Sam", likes_genres=["Drama", "Thriller"], mood=["Suspenseful"]),
                UserProfile(name="Jen", likes_genres=["Drama", "Crime"], mood=["Intense"]),
            ],
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Drama"],
        expected_best_score_min=7.0,
    ),
    # 5. Group of 2 with conflicting tastes
    GoldenCase(
        name="group_2_conflict",
        request=RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="Al", likes_genres=["Horror", "Thriller"], mood=["Dark"]),
                UserProfile(name="Bea", likes_genres=["Comedy", "Romance"], dislikes_genres=["Horror"], mood=["Funny"]),
            ],
        ),
        candidates=CANDIDATE_POOL,
        forbidden_genres=["Horror"],
    ),
    # 6. Solo with year range constraint
    GoldenCase(
        name="solo_90s_classics",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(
                name="Chris",
                likes_genres=["Drama", "Crime"],
                year_range=YearRange(min=1990, max=1999),
                mood=["Nostalgic"],
            )],
        ),
        candidates=CANDIDATE_POOL,
    ),
    # 7. Solo with context (date night)
    GoldenCase(
        name="solo_date_night",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="Dana", likes_genres=["Romance", "Drama", "Comedy"], mood=["Romantic"])],
            context=Context(occasion="date night", energy="medium"),
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Romance"],
    ),
    # 8. Group of 3
    GoldenCase(
        name="group_3_diverse",
        request=RecommendationRequest(
            mode="group",
            users=[
                UserProfile(name="A", likes_genres=["Action"], mood=["Adventurous"]),
                UserProfile(name="B", likes_genres=["Comedy"], mood=["Funny"]),
                UserProfile(name="C", likes_genres=["Drama"], mood=["Emotional"]),
            ],
        ),
        candidates=CANDIDATE_POOL,
        expected_diversity_min=3,
    ),
    # 9. Solo sci-fi nerd
    GoldenCase(
        name="solo_scifi",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(
                name="Neo",
                likes_genres=["Science Fiction"],
                mood=["Mind-bending"],
                favorite_directors=["Christopher Nolan"],
            )],
        ),
        candidates=CANDIDATE_POOL,
        expected_genre_overlap=["Science Fiction"],
    ),
    # 10. Solo free-text request
    GoldenCase(
        name="solo_free_text",
        request=RecommendationRequest(
            mode="solo",
            users=[UserProfile(name="Fern", likes_genres=["Drama"])],
            message="I want something that will make me think deeply about life and leaves a lasting impression.",
        ),
        candidates=CANDIDATE_POOL,
        expected_best_score_min=7.0,
    ),
]
