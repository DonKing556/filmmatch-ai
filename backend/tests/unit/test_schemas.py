from app.schemas.recommendation import RecommendationRequest, UserProfile


def test_solo_request_minimal():
    req = RecommendationRequest(
        mode="solo",
        users=[UserProfile(name="Mike", likes_genres=["thriller"])],
    )
    assert req.mode == "solo"
    assert len(req.users) == 1


def test_group_request():
    req = RecommendationRequest(
        mode="group",
        users=[
            UserProfile(name="Mike", likes_genres=["crime"]),
            UserProfile(name="Sarah", likes_genres=["comedy"]),
        ],
    )
    assert req.mode == "group"
    assert len(req.users) == 2
