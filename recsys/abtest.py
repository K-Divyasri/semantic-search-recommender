"""A/B testing two ranking strategies -- the part that makes this a system, not a demo.

Anyone can build a search box. What separates an engineer is being able to say *which*
ranking is better and prove it with a number. That's what this file does: it scores two
rankers on a labelled set of queries and declares a winner.

To score a ranking you need two things:

  1. **relevance labels** -- for each query, which movies are good answers, and how good.
     Here a movie is graded 2 (great) if it's on-topic AND popular, 1 (okay) if it's
     on-topic but obscure, and 0 otherwise. That definition -- "relevant means on-topic and
     something people actually watch" -- is deliberately why blending popularity into the
     ranking should win. (Real systems learn these labels from click data; ours are a
     synthetic stand-in, but the method is identical.)

  2. a **ranking metric** -- a number that's higher when the good answers are near the top.
     We use NDCG, which rewards putting the grade-2 items first, and precision@k, the plain
     fraction of the top-k that are relevant at all.

Run both rankers, average the metric over all queries, and the higher number wins.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .catalog import Movie
from .index import SearchIndex
from .ranking import RANKERS, Ranker

# Each query is genre-themed text (built from that genre's vocabulary) paired with the
# genre it's really asking for. Kept text-only so it reads like a real user query.
LABELLED_QUERIES: list[tuple[str, str]] = [
    ("alien spaceship galaxy invasion planet", "sci-fi"),
    ("love wedding paris heart romance", "romance"),
    ("haunted ghost demon nightmare cursed", "horror"),
    ("hilarious mixup awkward vacation prank", "comedy"),
    ("heist spy assassin conspiracy chase", "thriller"),
    ("dragon wizard magic quest kingdom", "fantasy"),
]

# A movie needs at least this popularity to count as a "great" (grade-2) answer.
_POPULAR = 60


def relevance(movie: Movie, target_genre: str) -> int:
    """Graded relevance: 2 = on-topic and popular, 1 = on-topic, 0 = off-topic."""
    if movie.genre != target_genre:
        return 0
    return 2 if movie.popularity >= _POPULAR else 1


def _dcg(relevances: list[int]) -> float:
    """Discounted cumulative gain: reward relevance, discounted by position."""
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


def ndcg_at_k(ranked: list[Movie], target_genre: str, k: int) -> float:
    """Normalised DCG in [0,1]: 1.0 means the ideal ordering for this query."""
    rels = [relevance(m, target_genre) for m in ranked[:k]]
    ideal = sorted(rels, reverse=True)
    idcg = _dcg(ideal)
    return _dcg(rels) / idcg if idcg > 0 else 0.0


def precision_at_k(ranked: list[Movie], target_genre: str, k: int) -> float:
    """Fraction of the top-k that are relevant at all (grade >= 1)."""
    rels = [relevance(m, target_genre) for m in ranked[:k]]
    return sum(1 for r in rels if r >= 1) / k if k else 0.0


@dataclass
class ABResult:
    """The outcome of the A/B: each ranker's mean metric, and the winner."""

    metric: str
    k: int
    scores: dict[str, float]        # ranker name -> mean metric across queries
    winner: str

    def report(self) -> str:
        lines = [f"A/B test on {len(LABELLED_QUERIES)} queries, metric={self.metric}@{self.k}:"]
        for name, score in sorted(self.scores.items(), key=lambda x: -x[1]):
            flag = "  <- winner" if name == self.winner else ""
            lines.append(f"  {name:<10} {score:.3f}{flag}")
        return "\n".join(lines)


def evaluate_ranker(index: SearchIndex, ranker: Ranker, k: int, metric: str) -> float:
    """Average a ranker's metric over all the labelled queries."""
    scorer = ndcg_at_k if metric == "ndcg" else precision_at_k
    total = 0.0
    for query, genre in LABELLED_QUERIES:
        ranked = [r.movie for r in index.search(query, k=k, ranker=ranker)]
        total += scorer(ranked, genre, k)
    return total / len(LABELLED_QUERIES)


def run_abtest(
    index: SearchIndex,
    rankers: dict[str, Ranker] | None = None,
    k: int = 10,
    metric: str = "ndcg",
) -> ABResult:
    """Score every ranker and return the winner (highest mean metric)."""
    rankers = rankers or RANKERS
    scores = {name: evaluate_ranker(index, r, k, metric) for name, r in rankers.items()}
    winner = max(scores, key=scores.get)
    return ABResult(metric=metric, k=k, scores=scores, winner=winner)
