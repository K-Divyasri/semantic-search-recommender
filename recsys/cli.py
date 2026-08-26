"""Run the search engine from the terminal.

    python -m recsys search "space adventure with aliens"
    python -m recsys search "love in paris" --genre romance --min-rating 7 --ranker blended
    python -m recsys similar "Crimson Nebula"          # "more like this"
    python -m recsys abtest                             # which ranker wins?

Offline by default (no key). The optional --explain uses a real model via LiteLLM.
"""

from __future__ import annotations

import argparse
import sys

from . import DEFAULT_K, GENRES
from .abtest import run_abtest
from .filters import Filters
from .index import SearchIndex
from .llm import explain
from .ranking import RANKERS


def _filters_from_args(args) -> Filters:
    return Filters(
        genres=args.genre or None,
        year_min=args.year_min,
        year_max=args.year_max,
        min_rating=args.min_rating,
    )


def _print_results(results, seed, args) -> None:
    if not results:
        print("(no matches -- try loosening the filters)")
        return
    for r in results:
        m = r.movie
        print(f"  [{m.id:>3}] {m.title:<26} {m.genre:<9} {m.year}  "
              f"rating {m.rating}  pop {m.popularity:>3}  "
              f"sim {r.similarity:.3f}  score {r.score:.3f}")
        if args.explain:
            print("        ->", explain(seed, m, offline=not args.real, model=args.model))


def _add_common(p) -> None:
    p.add_argument("--catalog", default=None, help="path to a movies CSV (else generated)")
    p.add_argument("--genre", action="append", choices=GENRES, help="filter by genre (repeatable)")
    p.add_argument("--year-min", type=int)
    p.add_argument("--year-max", type=int)
    p.add_argument("--min-rating", type=float)
    p.add_argument("--k", type=int, default=DEFAULT_K)
    p.add_argument("--ranker", choices=list(RANKERS), default="semantic")
    p.add_argument("--explain", action="store_true", help="add a one-line why (LLM)")
    p.add_argument("--real", action="store_true", help="use a real model for --explain")
    p.add_argument("--model", default=None)


def _cmd_search(args) -> None:
    index = SearchIndex.from_catalog(args.catalog)
    results = index.search(args.query, k=args.k, filters=_filters_from_args(args),
                           ranker=RANKERS[args.ranker])
    print(f"search: {args.query!r}  (ranker={args.ranker})")
    _print_results(results, args.query, args)


def _cmd_similar(args) -> None:
    index = SearchIndex.from_catalog(args.catalog)
    movie = index.find_by_title(args.title)
    if movie is None:
        print(f"no movie matching {args.title!r}. Try `search` first to find a title.")
        return
    results = index.similar(movie.id, k=args.k, filters=_filters_from_args(args),
                            ranker=RANKERS[args.ranker])
    print(f"more like: {movie.title!r} ({movie.genre}, {movie.year})")
    _print_results(results, movie.title, args)


def _cmd_abtest(args) -> None:
    index = SearchIndex.from_catalog(args.catalog)
    for metric in ("ndcg", "precision"):
        print(run_abtest(index, k=args.k, metric=metric).report())
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Semantic search & recommender over a movie catalog.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="semantic search by text query")
    p_search.add_argument("query")
    _add_common(p_search)
    p_search.set_defaults(func=_cmd_search)

    p_similar = sub.add_parser("similar", help="recommend movies like a given title")
    p_similar.add_argument("title", help="a title (or part of one)")
    _add_common(p_similar)
    p_similar.set_defaults(func=_cmd_similar)

    p_ab = sub.add_parser("abtest", help="score the ranking strategies and pick a winner")
    p_ab.add_argument("--catalog", default=None)
    p_ab.add_argument("--k", type=int, default=10)
    p_ab.set_defaults(func=_cmd_abtest)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
