from recsys.catalog import Movie
from recsys.ranking import make_blended, pure_semantic


def _m(mid, pop, rating):
    return Movie(id=mid, title=f"M{mid}", plot="x", genre="sci-fi",
                 year=2000, rating=rating, popularity=pop)


def test_pure_semantic_orders_by_similarity_only():
    cands = [(_m(1, 10, 6.0), 0.5), (_m(2, 99, 9.0), 0.9)]
    ranked = pure_semantic(cands)
    assert [m.id for m, _ in ranked] == [2, 1]     # 0.9 before 0.5


def test_blended_lifts_a_popular_high_rated_tie_breaker():
    # Two movies with the SAME similarity; the popular, higher-rated one should win.
    obscure = (_m(1, 5, 5.0), 0.7)
    popular = (_m(2, 95, 9.0), 0.7)
    ranked = make_blended()([obscure, popular])
    assert ranked[0][0].id == 2


def test_blended_still_respects_similarity_when_the_gap_is_large():
    # A much closer match beats a slightly more popular one -- similarity stays in charge.
    close = (_m(1, 20, 6.0), 0.95)
    popular_but_far = (_m(2, 90, 8.0), 0.30)
    ranked = make_blended()([close, popular_but_far])
    assert ranked[0][0].id == 1
