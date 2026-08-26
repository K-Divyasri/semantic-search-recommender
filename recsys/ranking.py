"""Ranking strategies -- deciding the final order.

Semantic similarity gives you a relevance score for every candidate. But "most similar"
isn't always "best to show". Two movies can be equally on-topic while one is a beloved
classic and the other is a forgotten flop -- most users want the classic. So ranking is a
*decision*: how to combine the similarity score with other signals (popularity, rating)
into one final order.

This module holds interchangeable ranking strategies. That they're swappable is the point:
in the next file we'll A/B test them and let a number decide which to ship.

A ranker takes candidates -- a list of `(movie, semantic_score)` -- and returns them
reordered as `(movie, final_score)`, best first.
"""

from __future__ import annotations

from collections.abc import Callable

from .catalog import Movie

Candidates = list[tuple[Movie, float]]
Ranker = Callable[[Candidates], Candidates]


def _rating_norm(rating: float) -> float:
    """Map a 5.0-9.5 rating onto 0-1 (clamped)."""
    return max(0.0, min(1.0, (rating - 5.0) / 4.5))


def pure_semantic(candidates: Candidates) -> Candidates:
    """Order by similarity alone -- the closest match wins, full stop."""
    return sorted(candidates, key=lambda x: -x[1])


def make_blended(w_sem: float = 0.6, w_pop: float = 0.25, w_rate: float = 0.15) -> Ranker:
    """A ranker that blends similarity with popularity and rating.

    The weights say how much each signal counts. The defaults keep similarity in charge
    (0.6) while letting popularity and rating break ties and lift crowd-pleasers.
    """

    def rank(candidates: Candidates) -> Candidates:
        scored = []
        for movie, sem in candidates:
            final = (
                w_sem * sem
                + w_pop * (movie.popularity / 100.0)
                + w_rate * _rating_norm(movie.rating)
            )
            scored.append((movie, final))
        return sorted(scored, key=lambda x: -x[1])

    return rank


# The default blended ranker, ready to use and to A/B against pure semantic.
blended = make_blended()

# The menu the CLI, the app, and the A/B test choose from.
RANKERS: dict[str, Ranker] = {
    "semantic": pure_semantic,
    "blended": blended,
}
