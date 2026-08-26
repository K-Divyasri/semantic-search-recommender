"""The search index -- where embeddings, filters, and ranking come together.

Build it once from the catalog: it embeds every movie's plot into a vector and keeps the
matrix. Then two methods do the whole product:

    search(query)        text -> the nearest movies ("find me something like...")
    similar(movie_id)    a movie -> the nearest OTHER movies ("more like this")

Both are the same operation underneath -- score every movie by cosine similarity to a query
vector -- differing only in where the query vector comes from (typed text, or an existing
movie). Both then apply the metadata filters and hand the survivors to a ranking strategy
for the final order.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import DEFAULT_K
from .catalog import Movie, load_or_generate
from .embedding import TfidfEmbedder, cosine_scores
from .filters import Filters, allowed_ids
from .ranking import Ranker, pure_semantic


@dataclass
class Result:
    """One result row: the movie, its final ranked score, and the raw similarity."""

    movie: Movie
    score: float        # after the ranking strategy (may blend in popularity/rating)
    similarity: float   # the raw semantic closeness, for transparency


class SearchIndex:
    """Embeds a catalog and serves semantic search + recommendations over it."""

    def __init__(self, movies: list[Movie], embedder=None) -> None:
        self.movies = movies
        self.embedder = embedder or TfidfEmbedder()
        # We embed the plot plus the genre word, so genre reinforces the vocabulary.
        docs = [f"{m.plot} {m.genre}" for m in movies]
        self.matrix = self.embedder.fit_transform(docs)
        self.by_id = {m.id: i for i, m in enumerate(movies)}

    @classmethod
    def from_catalog(cls, path=None, embedder=None) -> "SearchIndex":
        """Build an index from a catalog file (or the generated catalog if no file)."""
        return cls(load_or_generate(path), embedder=embedder)

    # -- the shared core ----------------------------------------------------- #
    def _candidates(self, query_vec, exclude_id, filters) -> list[tuple[Movie, float]]:
        sims = cosine_scores(self.matrix, query_vec)
        allowed = allowed_ids(self.movies, filters)
        cands = []
        for i, m in enumerate(self.movies):
            if m.id == exclude_id:      # never recommend a movie as similar to itself
                continue
            if m.id not in allowed:     # drop anything the filters exclude
                continue
            cands.append((m, float(sims[i])))
        return cands

    def _rank_and_wrap(self, query_vec, k, filters, ranker, exclude_id) -> list[Result]:
        cands = self._candidates(query_vec, exclude_id, filters)
        sim_map = {m.id: s for m, s in cands}       # keep raw similarity for display
        ranked = ranker(cands)[:k]
        return [Result(movie=m, score=final, similarity=sim_map[m.id]) for m, final in ranked]

    # -- the two public operations ------------------------------------------ #
    def search(
        self,
        query: str,
        k: int = DEFAULT_K,
        filters: Filters | None = None,
        ranker: Ranker = pure_semantic,
    ) -> list[Result]:
        """Semantic search: the movies whose plots are closest to the query text."""
        query_vec = self.embedder.transform([query])[0]
        return self._rank_and_wrap(query_vec, k, filters, ranker, exclude_id=None)

    def similar(
        self,
        movie_id: int,
        k: int = DEFAULT_K,
        filters: Filters | None = None,
        ranker: Ranker = pure_semantic,
    ) -> list[Result]:
        """Recommendations: the movies most like the given one ('more like this')."""
        i = self.by_id[movie_id]
        query_vec = self.matrix[i]
        return self._rank_and_wrap(query_vec, k, filters, ranker, exclude_id=movie_id)

    # -- small conveniences -------------------------------------------------- #
    def get(self, movie_id: int) -> Movie:
        return self.movies[self.by_id[movie_id]]

    def find_by_title(self, title: str) -> Movie | None:
        low = title.lower()
        for m in self.movies:
            if low in m.title.lower():
                return m
        return None
