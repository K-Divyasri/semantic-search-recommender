"""A Streamlit UI for the semantic search engine -- what you deploy for a public URL.

This file is deliberately thin: all the real work (embedding, search, filters, ranking,
the A/B test) lives in the `recsys` package. The app only draws the page -- a search box,
filter controls, a ranker switch, results, a "more like this" panel, and the A/B result.

Run it locally with:

    streamlit run web_app.py

Everything runs offline with the from-scratch embedder -- no key, no downloads.
"""

from __future__ import annotations

import streamlit as st

from recsys import DEFAULT_K, GENRES
from recsys.abtest import run_abtest
from recsys.filters import Filters
from recsys.index import SearchIndex
from recsys.ranking import RANKERS

st.set_page_config(page_title="Movie Semantic Search", page_icon=None, layout="wide")
st.title("Semantic Search & Recommender")
st.caption(
    "Search a movie catalog by meaning, filter by genre/year/rating, switch ranking "
    "strategies, and see which ranker wins an A/B test. Offline, no API key."
)


@st.cache_resource
def get_index() -> SearchIndex:
    return SearchIndex.from_catalog()


index = get_index()

with st.sidebar:
    st.header("Filters & ranking")
    genres = st.multiselect("Genres", GENRES)
    years = [m.year for m in index.movies]
    yr = st.slider("Year range", min(years), max(years), (min(years), max(years)))
    min_rating = st.slider("Minimum rating", 5.0, 9.5, 5.0, 0.5)
    k = st.slider("Results", 1, 15, DEFAULT_K)
    ranker_name = st.radio("Ranking strategy", list(RANKERS), horizontal=True)

filters = Filters(
    genres=genres or None,
    year_min=yr[0],
    year_max=yr[1],
    min_rating=min_rating if min_rating > 5.0 else None,
)


def _rows(results):
    return [
        {
            "id": r.movie.id,
            "title": r.movie.title,
            "genre": r.movie.genre,
            "year": r.movie.year,
            "rating": r.movie.rating,
            "popularity": r.movie.popularity,
            "similarity": round(r.similarity, 3),
            "score": round(r.score, 3),
        }
        for r in results
    ]


tab_search, tab_similar, tab_ab = st.tabs(["Search", "More like this", "A/B test"])

with tab_search:
    query = st.text_input("Search by meaning", value="space adventure with aliens")
    if query:
        results = index.search(query, k=k, filters=filters, ranker=RANKERS[ranker_name])
        st.caption(f"{len(results)} results, ranked by **{ranker_name}**")
        st.dataframe(_rows(results), use_container_width=True)

with tab_similar:
    titles = {f"{m.title} ({m.genre}, {m.year})": m.id for m in index.movies}
    pick = st.selectbox("Pick a movie", list(titles))
    if pick:
        mid = titles[pick]
        results = index.similar(mid, k=k, filters=filters, ranker=RANKERS[ranker_name])
        st.caption(f"Movies most like **{pick}**")
        st.dataframe(_rows(results), use_container_width=True)

with tab_ab:
    st.write(
        "Two ranking strategies scored on a labelled set of queries. **NDCG** rewards "
        "putting the best answers first; **precision@k** just counts how many of the "
        "top-k are on-topic."
    )
    for metric in ("ndcg", "precision"):
        res = run_abtest(index, k=10, metric=metric)
        st.subheader(f"{metric}@10")
        st.dataframe(
            [{"ranker": name, "score": round(s, 3), "winner": "yes" if name == res.winner else ""}
             for name, s in sorted(res.scores.items(), key=lambda x: -x[1])],
            use_container_width=True,
        )
    st.info(
        "Precision often ties (both rankers return on-topic results), while NDCG shows the "
        "blended ranker winning -- because it puts the popular, on-topic movies first. The "
        "metric you choose decides whether you can even see the improvement."
    )
