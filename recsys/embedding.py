"""Turning text into vectors.

Search and recommendation both need every movie's description as a **vector** -- a point in
space where "close together" means "about the same thing". This module builds those
vectors.

The default is a **TF-IDF** embedder, built from scratch with numpy:

  * TF (term frequency): a word matters more to a document the more it appears in it.
  * IDF (inverse document frequency): a word matters more the RARER it is across the whole
    catalog -- "the" is everywhere and tells you nothing; "wormhole" is rare and tells you a
    lot.

Multiply them, normalise each vector to unit length, and cosine similarity (a dot product)
measures closeness. It's lexical -- it keys off the actual words -- which is honest and works
well when descriptions in the same genre share vocabulary. For deeper meaning (catching that
"space" and "cosmos" are related even though the letters differ) you'd swap in real sentence
embeddings; an optional `minilm` backend does exactly that.
"""

from __future__ import annotations

import math
import re

import numpy as np

_STOP = {
    "a", "an", "the", "of", "and", "to", "in", "is", "it", "with", "for", "on",
    "story", "where", "leads", "who", "that", "this",
}


def tokenize(text: str) -> list[str]:
    """Lowercase, split into words, drop stopwords, and lightly stem plurals."""
    tokens = []
    for w in re.findall(r"[a-z']+", text.lower()):
        if w in _STOP:
            continue
        if len(w) > 3 and w.endswith("s"):   # aliens -> alien, robots -> robot
            w = w[:-1]
        tokens.append(w)
    return tokens


class TfidfEmbedder:
    """A from-scratch TF-IDF vectoriser. Fit it on the catalog, then transform any text."""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}
        self.idf: np.ndarray | None = None
        self.name = "tfidf"

    def fit(self, corpus: list[str]) -> "TfidfEmbedder":
        # Build the vocabulary and each word's document frequency.
        df: dict[str, int] = {}
        for text in corpus:
            for w in set(tokenize(text)):
                df[w] = df.get(w, 0) + 1
        self.vocab = {w: i for i, w in enumerate(sorted(df))}
        n_docs = len(corpus)
        idf = np.zeros(len(self.vocab), dtype=np.float64)
        for w, i in self.vocab.items():
            # smoothed idf: rarer words get a higher weight
            idf[i] = math.log((1 + n_docs) / (1 + df[w])) + 1
        self.idf = idf
        return self

    def transform(self, texts: list[str]) -> np.ndarray:
        """Turn texts into an (n_texts, vocab) matrix of L2-normalised TF-IDF vectors."""
        assert self.idf is not None, "call fit() first"
        rows = np.zeros((len(texts), len(self.vocab)), dtype=np.float64)
        for r, text in enumerate(texts):
            counts: dict[int, int] = {}
            toks = tokenize(text)
            for w in toks:
                j = self.vocab.get(w)
                if j is not None:
                    counts[j] = counts.get(j, 0) + 1
            if not counts:
                continue
            total = len(toks)
            for j, c in counts.items():
                rows[r, j] = (c / total) * self.idf[j]   # tf * idf
        # L2-normalise each row so cosine similarity is a plain dot product.
        norms = np.linalg.norm(rows, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return rows / norms

    def fit_transform(self, corpus: list[str]) -> np.ndarray:
        return self.fit(corpus).transform(corpus)


class MiniLMEmbedder:
    """Optional real sentence embeddings via sentence-transformers (a download the first time)."""

    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415 (lazy)

        self._model = SentenceTransformer(model)
        self.name = "minilm"

    def fit(self, corpus: list[str]) -> "MiniLMEmbedder":
        return self  # nothing to fit; the model is pretrained

    def transform(self, texts: list[str]) -> np.ndarray:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float64)

    def fit_transform(self, corpus: list[str]) -> np.ndarray:
        return self.transform(corpus)


def build_embedder(backend: str = "tfidf"):
    """Pick an embedder. 'tfidf' (default, offline) or 'minilm' (real, opt-in download)."""
    if backend == "minilm":
        return MiniLMEmbedder()
    return TfidfEmbedder()


def cosine_scores(matrix: np.ndarray, query_vec: np.ndarray) -> np.ndarray:
    """Cosine similarity of every row in `matrix` against `query_vec` (both unit-normalised)."""
    return matrix @ query_vec
