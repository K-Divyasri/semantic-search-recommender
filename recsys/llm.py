"""Optional LLM touch: a one-line "why you might like this".

The search and recommendations are pure vector maths -- no LLM needed, and that's the
right default. But a nice product touch is a short, human explanation of *why* something
was recommended. That's a job an LLM does well.

As everywhere in this track, it's two modes behind one function: an OFFLINE template that
needs no key, and a real LiteLLM call when you want polish. The explanation is a garnish --
the ranking is the substance -- so the offline version is perfectly fine.
"""

from __future__ import annotations

import os

from .catalog import Movie

DEFAULT_MODEL = os.environ.get("RECSYS_MODEL", "gemini/gemini-1.5-flash")


def explain(seed: str, movie: Movie, *, offline: bool = True, model: str | None = None) -> str:
    """One sentence on why `movie` fits `seed` (a search query or a 'because you watched X')."""
    if offline:
        return (
            f"A {movie.genre} pick ({movie.year}, rated {movie.rating}/10) that matches "
            f"your interest in {seed!r}."
        )
    from litellm import completion  # noqa: PLC0415  (lazy on purpose)

    prompt = (
        f"In one short, friendly sentence, tell a user why the movie "
        f"'{movie.title}' -- a {movie.genre} film from {movie.year} -- is a good match "
        f"for their interest in: {seed}. Don't invent plot details."
    )
    resp = completion(
        model=model or DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content or ""
