# Semantic Search Recommender

**Semantic search and recommendations over a movie catalog**: search by meaning, get
"more like this," filter by genre/year/rating, switch ranking strategies, and **A/B test
which ranker wins**.

**Problem:** Keyword search misses "space adventure with aliens" if the text says
"interstellar"; you need to search by *meaning*. And once results are relevant, the order
still matters: the closest match isn't always the best thing to show. This project builds
both the meaning-based retrieval and the ranking on top of it, and measures the ranking.

**Skills demonstrated:** semantic search, embeddings (TF-IDF from scratch), recommendations
("find things like this"), metadata filtering, ranking strategies, and A/B testing rankers
with a proper metric (NDCG / precision@k).

**Tech stack:** Python 3.10+, numpy (the only core dependency), optional
sentence-transformers for real embeddings, optional LiteLLM for explanations, Streamlit for
the UI, pytest. Runs **offline with no API key and no model download** by default.

## Run it

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m recsys search "space adventure with aliens"
python -m recsys search "love in paris" --genre romance --min-rating 7 --ranker blended
python -m recsys similar "Crimson Nebula"        # more like this
python -m recsys abtest                           # which ranker wins?
```

## The headline result

The A/B test scores two rankers on a labelled set of queries:

```
A/B test on 6 queries, metric=ndcg@10:
  blended    0.974  <- winner
  semantic   0.920

metric=precision@10:
  semantic   1.000
  blended    1.000
```

**Blended wins on NDCG**: blending popularity and rating into the order lifts the popular,
on-topic movies to the top. Precision@10 *ties*, because both rankers return on-topic
results; it just can't see the ordering improvement. The metric you choose decides whether
you can even measure the win, which is the real lesson.

## Run the tests

```powershell
pytest
```

All 23 tests pass with **no API key and no downloads** (just numpy), including the one that
proves the done-when: the A/B test picks the blended ranker.

## The web demo

```powershell
pip install streamlit
streamlit run web_app.py
```

A search box, filter controls, a ranker switch, a "more like this" tab, and the A/B result.
Deploy it free, see `hosting/HOSTING_GUIDE.md`.

## How it fits together

```
recsys/
  catalog.py     the movie dataset (deterministic generator + load/save)
  embedding.py   text -> vector (from-scratch TF-IDF; optional real sentence embeddings)
  index.py       build vectors; search() and similar(); applies filters + a ranker
  filters.py     the structured metadata constraints (genre / year / rating)
  ranking.py     ranking strategies: pure semantic vs blended-with-popularity (the choice)
  abtest.py      score two rankers on a labelled set, declare a winner (the star)
  llm.py         optional one-line "why recommended" (offline template or LiteLLM)
  cli.py         search / similar / abtest
web_app.py       the Streamlit UI (imports the package, adds no new logic)
```

## What I learned

- Search and recommendations are the same operation, nearest vectors, differing only in
  whether the query vector comes from typed text or an existing item.
- A real search product pairs a *fuzzy* relevance score with *crisp* metadata filters.
- Ranking is a decision, not a given: blending popularity/rating with similarity usually
  beats pure similarity, and you should prove it, not assume it.
- **A/B testing needs labels and a metric.** NDCG rewards ordering; precision@k doesn't,
  so the wrong metric can hide a real improvement.
