from recsys.filters import Filters
from recsys.ranking import RANKERS


def test_search_returns_k_results_sorted_by_score(index):
    results = index.search("alien spaceship galaxy invasion", k=5)
    assert len(results) == 5
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_finds_the_right_genre(index):
    # A space query should surface mostly sci-fi movies at the top.
    results = index.search("alien spaceship galaxy invasion planet", k=5)
    genres = [r.movie.genre for r in results]
    assert genres.count("sci-fi") >= 4


def test_recommend_excludes_the_movie_itself(index):
    seed = index.search("dragon wizard magic quest", k=1)[0].movie
    recs = index.similar(seed.id, k=5)
    assert all(r.movie.id != seed.id for r in recs)


def test_recommend_returns_similar_genre(index):
    seed = index.search("haunted ghost demon nightmare", k=1)[0].movie
    recs = index.similar(seed.id, k=5)
    # "More like this" for a horror movie should mostly be horror.
    assert sum(1 for r in recs if r.movie.genre == seed.genre) >= 3


def test_genre_filter_restricts_results(index):
    results = index.search("love wedding paris", k=8, filters=Filters(genres=["romance"]))
    assert all(r.movie.genre == "romance" for r in results)


def test_rating_and_year_filters(index):
    f = Filters(min_rating=8.0, year_min=2000)
    results = index.search("heist spy assassin", k=10, filters=f)
    assert all(r.movie.rating >= 8.0 and r.movie.year >= 2000 for r in results)


def test_ranker_changes_the_order(index):
    q = "alien spaceship galaxy invasion planet"
    sem = [r.movie.id for r in index.search(q, k=10, ranker=RANKERS["semantic"])]
    blend = [r.movie.id for r in index.search(q, k=10, ranker=RANKERS["blended"])]
    # Same candidate pool, but the blended ranker orders them differently.
    assert sem != blend
