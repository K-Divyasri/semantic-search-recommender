"""The movie catalog -- the data we search and recommend over.

A recommender needs a catalog. Rather than ship a big data file (or make you download
one), we generate a deterministic, believable set of movies in code: each has a title, a
one-line plot, a genre, a year, an IMDb-style rating, and a popularity score. The plots
are built from genre-specific vocabulary, so a horror movie really does read differently
from a romance -- which is exactly what lets semantic search tell them apart.

It's fully deterministic (a fixed random seed), so the catalog, the vectors, and the tests
are identical every run.
"""

from __future__ import annotations

import csv
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from . import GENRES

# Genre-specific word pools. Because these barely overlap, movies of the same genre end up
# with similar vectors and different genres end up far apart -- the whole basis of the demo.
_PLOT_WORDS: dict[str, list[str]] = {
    "sci-fi": ["spaceship", "alien", "galaxy", "robot", "planet", "starship", "android",
               "wormhole", "colony", "astronaut", "invasion", "cybernetic", "quantum", "orbit"],
    "romance": ["love", "wedding", "heart", "romance", "kiss", "paris", "affair", "letters",
                "longing", "reunited", "sweetheart", "courtship", "vow", "embrace"],
    "horror": ["haunted", "ghost", "demon", "blood", "nightmare", "cursed", "killer",
               "darkness", "possession", "witch", "asylum", "grave", "terror", "monster"],
    "comedy": ["hilarious", "mixup", "prank", "misadventure", "awkward", "roommate",
               "vacation", "blunder", "office", "dating", "chaos", "wager", "disguise"],
    "thriller": ["heist", "spy", "conspiracy", "assassin", "chase", "detective", "hostage",
                 "betrayal", "undercover", "murder", "fugitive", "evidence", "ransom"],
    "fantasy": ["dragon", "kingdom", "wizard", "magic", "quest", "sword", "prophecy", "elf",
                "enchanted", "throne", "sorcerer", "realm", "knight", "spellbook"],
}

_TITLE_ADJ = ["Last", "Silent", "Broken", "Crimson", "Hidden", "Eternal", "Frozen",
              "Golden", "Savage", "Distant", "Burning", "Forgotten", "Wild", "Secret"]
_TITLE_NOUN = {
    "sci-fi": ["Horizon", "Signal", "Orbit", "Colony", "Nebula", "Protocol"],
    "romance": ["Letter", "Promise", "Summer", "Waltz", "Rendezvous", "Heart"],
    "horror": ["Hollow", "Whisper", "Ritual", "Crypt", "Shadow", "Descent"],
    "comedy": ["Mixup", "Getaway", "Roommate", "Wager", "Fiasco", "Holiday"],
    "thriller": ["Contract", "Informant", "Deadline", "Payload", "Verdict", "Pursuit"],
    "fantasy": ["Throne", "Prophecy", "Realm", "Blade", "Crown", "Spell"],
}


@dataclass
class Movie:
    """One catalog item. `plot` is the text we embed; the rest are metadata for filters."""

    id: int
    title: str
    plot: str
    genre: str
    year: int
    rating: float       # 5.0 - 9.5, IMDb-style
    popularity: int     # 1 - 100, a stand-in for how much people watch it


def _make_plot(genre: str, rng: random.Random) -> str:
    words = rng.sample(_PLOT_WORDS[genre], 5)
    return (
        f"A {genre} story of {words[0]} and {words[1]}, where a {words[2]} "
        f"leads to {words[3]} and {words[4]}."
    )


def generate_catalog(n_per_genre: int = 30, seed: int = 42) -> list[Movie]:
    """Build a deterministic catalog of movies -- the same every time (fixed seed)."""
    rng = random.Random(seed)
    movies: list[Movie] = []
    mid = 0
    for genre in GENRES:
        for _ in range(n_per_genre):
            title = (
                f"The {rng.choice(_TITLE_ADJ)} {rng.choice(_TITLE_NOUN[genre])}"
            )
            movies.append(
                Movie(
                    id=mid,
                    title=title,
                    plot=_make_plot(genre, rng),
                    genre=genre,
                    year=rng.randint(1980, 2024),
                    rating=round(rng.uniform(5.0, 9.5), 1),
                    popularity=rng.randint(1, 100),
                )
            )
            mid += 1
    return movies


# --------------------------------------------------------------------------- #
#  Load / save                                                               #
# --------------------------------------------------------------------------- #
_FIELDS = ["id", "title", "plot", "genre", "year", "rating", "popularity"]


def save_catalog(movies: list[Movie], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS)
        writer.writeheader()
        for m in movies:
            writer.writerow(asdict(m))
    return path


def load_catalog(path: str | Path) -> list[Movie]:
    movies = []
    with Path(path).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movies.append(
                Movie(
                    id=int(row["id"]),
                    title=row["title"],
                    plot=row["plot"],
                    genre=row["genre"],
                    year=int(row["year"]),
                    rating=float(row["rating"]),
                    popularity=int(row["popularity"]),
                )
            )
    return movies


def load_or_generate(path: str | Path | None = None) -> list[Movie]:
    """Load the catalog from `path` if it exists, otherwise generate it fresh."""
    if path is not None and Path(path).exists():
        return load_catalog(path)
    return generate_catalog()
