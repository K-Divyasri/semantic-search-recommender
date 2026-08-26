"""recsys -- a semantic search engine and recommender over a movie catalog.

Two features that look different but share an engine:

  SEARCH        you type "space adventure with aliens" and get the movies whose
                descriptions are closest in MEANING -- not just keyword matches.

  RECOMMEND     you point at a movie and get "more like this" -- the same closeness,
                but measured from an item instead of a query.

Both come down to one idea: turn every movie's description into a vector (a list of
numbers that captures what it's about), and find the nearest vectors. Everything else in
this project is what turns that raw closeness into a good product:

    filters       let the user narrow by genre, year, or rating (structured constraints
                  on top of the fuzzy semantic match)
    ranking       decide the final order -- pure similarity, or similarity blended with
                  popularity and rating, because the closest match isn't always the best
                  thing to show
    A/B testing    measure which ranking strategy is actually better, with a number,
                  instead of arguing about it (the part that separates a demo from a
                  system you can improve on purpose)

The pieces, each readable on its own:

    catalog.py     the movie dataset (a deterministic generator + load/save)
    embedding.py   text -> vector (a TF-IDF embedder; optional real sentence embeddings)
    index.py       build the vectors and do search / recommend, with filters
    filters.py     the structured metadata constraints
    ranking.py     ranking strategies that combine similarity with other signals
    abtest.py      score two rankers on a labelled set and declare a winner (the star)
    cli.py         search / similar / abtest from the terminal
    web_app.py     the Streamlit search-and-recommend UI

Everything runs OFFLINE with a from-scratch embedder -- no model download, no API key.
An optional sentence-transformers backend gives sharper meaning when you want it.
"""

from __future__ import annotations

# The genres in our catalog. Kept small and distinct so semantic clustering is easy to
# see: a horror plot and a romance plot really don't share vocabulary.
GENRES = ["sci-fi", "romance", "horror", "comedy", "thriller", "fantasy"]

# How many results to return by default from a search or a recommendation.
DEFAULT_K = 5

__all__ = ["GENRES", "DEFAULT_K"]
