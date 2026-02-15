from app.services.tmdb_service import GENRE_MAP, GENRE_NAME_TO_ID, MovieCandidate


def test_genre_map_has_common_genres():
    assert 28 in GENRE_MAP  # Action
    assert 35 in GENRE_MAP  # Comedy
    assert 18 in GENRE_MAP  # Drama
    assert 27 in GENRE_MAP  # Horror
    assert 878 in GENRE_MAP  # Science Fiction


def test_genre_name_to_id_lookup():
    assert GENRE_NAME_TO_ID["action"] == 28
    assert GENRE_NAME_TO_ID["comedy"] == 35
    assert GENRE_NAME_TO_ID["horror"] == 27
    assert GENRE_NAME_TO_ID["science fiction"] == 878


def test_movie_candidate_to_prompt_string():
    candidate = MovieCandidate(
        tmdb_id=550,
        title="Fight Club",
        overview="An insomniac office worker and a soap salesman form an underground fight club.",
        release_date="1999-10-15",
        genres=["Drama", "Thriller"],
        genre_ids=[18, 53],
        vote_average=8.4,
        vote_count=25000,
        popularity=50.0,
        runtime=139,
        poster_path="/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        backdrop_path="/hZkgoQYus5dXo3H8T7Uef6DNknx.jpg",
        original_language="en",
        director_names=["David Fincher"],
        cast_names=["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
    )
    prompt = candidate.to_prompt_string()
    assert "TMDB ID: 550" in prompt
    assert "Fight Club" in prompt
    assert "1999" in prompt
    assert "Drama" in prompt
    assert "David Fincher" in prompt
    assert "Brad Pitt" in prompt
    assert "139 min" in prompt


def test_movie_candidate_unknown_runtime():
    candidate = MovieCandidate(
        tmdb_id=1,
        title="Test",
        overview="Test movie",
        release_date=None,
        genres=[],
        genre_ids=[],
        vote_average=0,
        vote_count=0,
        popularity=0,
        runtime=None,
        poster_path=None,
        backdrop_path=None,
        original_language="en",
        director_names=[],
        cast_names=[],
    )
    prompt = candidate.to_prompt_string()
    assert "Runtime: Unknown" in prompt
    assert "Unknown)" in prompt  # year unknown
