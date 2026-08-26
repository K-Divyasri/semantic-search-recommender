from recsys.abtest import (
    ndcg_at_k,
    precision_at_k,
    relevance,
    run_abtest,
)
from recsys.catalog import Movie


def _m(genre, pop):
    return Movie(id=0, title="t", plot="x", genre=genre, year=2000, rating=8.0, popularity=pop)


def test_graded_relevance():
    assert relevance(_m("sci-fi", 90), "sci-fi") == 2     # on-topic + popular
    assert relevance(_m("sci-fi", 10), "sci-fi") == 1     # on-topic, obscure
    assert relevance(_m("romance", 90), "sci-fi") == 0    # off-topic


def test_ndcg_rewards_putting_the_best_first():
    good_first = [_m("sci-fi", 90), _m("sci-fi", 10)]   # grade 2 then 1
    bad_first = [_m("sci-fi", 10), _m("sci-fi", 90)]    # grade 1 then 2
    assert ndcg_at_k(good_first, "sci-fi", 2) > ndcg_at_k(bad_first, "sci-fi", 2)


def test_precision_counts_any_relevant():
    ranked = [_m("sci-fi", 90), _m("romance", 90), _m("sci-fi", 10), _m("horror", 5)]
    assert precision_at_k(ranked, "sci-fi", 4) == 0.5     # 2 of 4 are sci-fi


def test_the_ab_test_picks_the_blended_ranker_on_ndcg(index):
    # THE done-when: an A/B comparison, with a number, shows which ranking wins.
    result = run_abtest(index, k=10, metric="ndcg")
    assert set(result.scores) == {"semantic", "blended"}
    assert result.winner == "blended"                    # blending popularity wins
    assert result.scores["blended"] > result.scores["semantic"]


def test_ndcg_scores_are_in_range(index):
    result = run_abtest(index, k=10, metric="ndcg")
    assert all(0.0 <= s <= 1.0 for s in result.scores.values())
