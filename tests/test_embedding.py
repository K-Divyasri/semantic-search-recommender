import numpy as np

from recsys.embedding import TfidfEmbedder, cosine_scores, tokenize


def test_tokenize_lowercases_stems_and_drops_stopwords():
    toks = tokenize("The aliens and the Robots")
    assert "the" not in toks and "and" not in toks
    assert "alien" in toks and "robot" in toks     # plurals stemmed


def test_vectors_are_unit_normalised():
    emb = TfidfEmbedder()
    mat = emb.fit_transform(["alien spaceship galaxy", "love wedding heart"])
    norms = np.linalg.norm(mat, axis=1)
    assert np.allclose(norms, 1.0)


def test_similar_texts_score_higher_than_unrelated():
    emb = TfidfEmbedder()
    corpus = ["alien spaceship galaxy planet", "love wedding paris heart",
              "alien robot invasion planet"]
    mat = emb.fit_transform(corpus)
    q = emb.transform(["alien planet invasion"])[0]
    sims = cosine_scores(mat, q)
    # The two sci-fi docs should beat the romance doc.
    assert sims[0] > sims[1] and sims[2] > sims[1]


def test_embedding_is_deterministic():
    emb1 = TfidfEmbedder().fit_transform(["alien spaceship", "love heart"])
    emb2 = TfidfEmbedder().fit_transform(["alien spaceship", "love heart"])
    assert np.array_equal(emb1, emb2)
