"""Metadata filters -- the structured constraints on top of the fuzzy semantic match.

Semantic similarity is fuzzy: it ranks everything by closeness. But users also have hard
requirements -- "only horror", "nothing before 2000", "rating at least 7". Those are
**filters**: exact conditions on the metadata that either let a movie through or don't.

A real search product is always this pairing: a fuzzy relevance score, narrowed by crisp
filters. This module is the crisp half.
"""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import Movie


@dataclass
class Filters:
    """A set of optional constraints. `None` means 'don't care about this one'."""

    genres: list[str] | None = None       # keep only these genres
    year_min: int | None = None
    year_max: int | None = None
    min_rating: float | None = None

    def allows(self, movie: Movie) -> bool:
        if self.genres is not None and movie.genre not in self.genres:
            return False
        if self.year_min is not None and movie.year < self.year_min:
            return False
        if self.year_max is not None and movie.year > self.year_max:
            return False
        if self.min_rating is not None and movie.rating < self.min_rating:
            return False
        return True

    def is_empty(self) -> bool:
        return (self.genres is None and self.year_min is None
                and self.year_max is None and self.min_rating is None)


def allowed_ids(movies: list[Movie], filters: Filters | None) -> set[int]:
    """The ids of movies that pass the filter (all of them if there's no filter)."""
    if filters is None or filters.is_empty():
        return {m.id for m in movies}
    return {m.id for m in movies if filters.allows(m)}
