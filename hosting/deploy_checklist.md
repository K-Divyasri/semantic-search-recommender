# Deploy checklist — Semantic Search & Recommender

This is the project's "definition of done." Walk it top to bottom. Don't tick a box you
haven't actually verified by running the command — "should work" isn't the same as "works."

## Runs locally

- [ ] Fresh virtual environment, dependencies installed cleanly (from the repo root):
      `python -m venv .venv ; .\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt`
- [ ] Semantic search works offline, no API key:
      `python -m recsys search "space adventure with aliens"` prints ranked results.
- [ ] Recommendations work offline:
      `python -m recsys similar "Crimson Nebula"` prints "more like this" results.
- [ ] The A/B test runs offline:
      `python -m recsys abtest` prints the ndcg@10 and precision@10 tables with a winner.
- [ ] The app runs offline in a browser:
      `streamlit run web_app.py` opens the page at `http://localhost:8501`, populated on load —
      the Search, More like this, and A/B test tabs all work with no data files and no key.
- [ ] (Optional) `python -m recsys search "..." --explain --real` adds an LLM "why" line with a
      key in `.env`, OR is left alone — offline is the default and needs nothing.

## Tests pass

- [ ] `pytest` run from the repo root is all green (23 tests, all offline, no key).
- [ ] You ran it in the fresh venv, not just your everyday one, so you know the deps are complete
      (the one that matters is numpy — it's in `requirements.txt`).

## README is recruiter-ready

- [ ] A root `README.md` exists and covers: the problem, what the project does, how to run it,
      and what you learned.
- [ ] A **screenshot or GIF** is embedded — the search results table and/or the **A/B test tab**
      showing the blended ranker winning NDCG (`docs/search.png`, `docs/abtest.png`, or a short
      GIF). The "blended wins NDCG" shot is the memorable visual; show it.
- [ ] The live demo URL is near the top (add it after Step 6).
- [ ] The CI status badge is at the top.

## Secrets are clean

- [ ] The root `.gitignore` contains `.env`, `*.csv`,
      `*.npz`, `.venv/`, `__pycache__/`, `.pytest_cache/`.
- [ ] `git status` shows `.env` is NOT tracked.
- [ ] `git ls-files` output contains NO `.env` (only `.env.example`) and NO `.csv` file
      (e.g. `data/movies.csv`). If any is there, remove it — see the hosting guide's
      troubleshooting section; for a committed `.env`, also rotate the key.
- [ ] No API key is hardcoded anywhere in the source.

## Pushed to GitHub

- [ ] Repo created empty on github.com (no auto README/license), named
      `semantic-search-recommender`, public.
- [ ] `git init` → `git add .` → `git commit` → `git branch -M main` →
      `git remote add origin ...` → `git push -u origin main` all done (from the project root).
- [ ] Files visible on the GitHub repo page after a refresh.

## CI is green

- [ ] `.github/workflows/ci.yml` is committed and pushed.
- [ ] The Actions tab shows a completed run with a green checkmark.
- [ ] The run used NO secrets (the tests are offline) — confirm it passed without any API key
      configured. That's a selling point; mention it in the README.
- [ ] If it was red, you read the log and fixed the cause (usually a missing dep in
      `requirements.txt` - most likely numpy), then re-ran to green.

## Live demo

- [ ] Deployed free to Streamlit Community Cloud (main file path
      `web_app.py`) or Hugging Face Spaces.
- [ ] Opening the public URL loads the page fully populated — search, filters, "more like this",
      and the A/B result all work with no committed data and no key.
- [ ] The heavy `sentence-transformers` extra is left commented out in `requirements.txt` so the
      free host build doesn't time out.
- [ ] (Only if you enabled the optional LLM explanation) the API key is set as a host **Secret**
      (`GEMINI_API_KEY`) — never in code — and you chose the free Gemini tier, or accepted the
      cost of a paid model knowingly.
- [ ] The live demo URL is added to the top of the README.

## Repo pinned

- [ ] `semantic-search-recommender` is pinned on your GitHub profile so it shows up first.

When every box is ticked, the project is done and presentable. Send the repo link with
confidence.
