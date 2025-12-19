from __future__ import annotations

import argparse

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.prefix import PrefixPredictor
from aac.ranking.learning import LearningRanker


def build_engine() -> AutocompleteEngine:
    """
    Constructs the autocomplete engine.

    Centralized so CLI behavior is deterministic and testable.
    """
    history = History()

    return AutocompleteEngine(
        predictors=[
            PrefixPredictor(["hello", "help", "helium", "hero"]),
        ],
        ranker=LearningRanker(history),
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="aac")
    subparsers = parser.add_subparsers(dest="command", required=True)

    suggest = subparsers.add_parser("suggest")
    suggest.add_argument("prefix", type=str)
    suggest.add_argument(
        "--explain",
        action="store_true",
        help="Show ranking explanations",
    )

    args = parser.parse_args()

    engine = build_engine()

    if args.command == "suggest":
        handle_suggest(engine, args.prefix, args.explain)


def handle_suggest(
    engine: AutocompleteEngine,
    prefix: str,
    explain: bool,
) -> None:
    suggestions = engine.suggest(prefix)

    if not explain:
        for s in suggestions:
            print(s.value)
        return

    explanations = engine.explain(prefix)

    for suggestion, explanation in zip(
        suggestions,
        explanations,
        strict=True,
    ):
        print(suggestion.value)
        print(
            f"  base={explanation.base_score:.2f} "
            f"+ history={explanation.history_boost:.2f} "
            f"=> {explanation.final_score:.2f}"
        )
