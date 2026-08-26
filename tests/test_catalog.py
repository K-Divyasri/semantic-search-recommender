from recsys import GENRES
from recsys.catalog import generate_catalog, load_catalog, save_catalog


def test_catalog_is_deterministic():
    a = generate_catalog()
    b = generate_catalog()
    assert [m.title for m in a] == [m.title for m in b]
    assert [m.plot for m in a] == [m.plot for m in b]


def test_catalog_has_all_genres_and_valid_fields():
    movies = generate_catalog(n_per_genre=10)
    assert len(movies) == 10 * len(GENRES)
    assert {m.genre for m in movies} == set(GENRES)
    for m in movies:
        assert m.plot and m.title
        assert 1980 <= m.year <= 2024
        assert 5.0 <= m.rating <= 9.5
        assert 1 <= m.popularity <= 100


def test_ids_are_unique_and_sequential():
    movies = generate_catalog()
    ids = [m.id for m in movies]
    assert ids == list(range(len(movies)))


def test_save_then_load_roundtrip(tmp_path):
    movies = generate_catalog(n_per_genre=5)
    path = save_catalog(movies, tmp_path / "movies.csv")
    loaded = load_catalog(path)
    assert len(loaded) == len(movies)
    assert loaded[0].title == movies[0].title
    assert loaded[3].rating == movies[3].rating
