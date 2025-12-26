from __future__ import annotations

import argparse
from pathlib import Path

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.prefix import PrefixPredictor
from aac.ranking.learning import LearningRanker
from aac.storage.json_history import JsonHistory
# from aac.storage.json_store import JsonHistoryStore - #TODO: use JsonHistoryStore or JsonHistory

DEFAULT_HISTORY_PATH = Path(".aac_history.json")


def build_engine(history: History | None = None) -> AutocompleteEngine:
    """
    Builds the autocomplete engine.

    Centralized so CLI behavior is testable,
    repeatable, and consistent with production usage.
    """
    history = history or JsonHistory(DEFAULT_HISTORY_PATH)

    return AutocompleteEngine(
        predictors=[
            PrefixPredictor(
                vocabulary=["hello", "help", "helium", "hero"],
            ),
        ],
        ranker=LearningRanker(history),
        history=history,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aac",
        description="Adaptive autocomplete engine with learning and explainability",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # SUGGEST
    suggest = subparsers.add_parser(
        "suggest",
        help="Generate autocomplete suggestions",
    )
    suggest.add_argument("text", type=str)
    suggest.add_argument(
        "--explain",
        action="store_true",
        help="Show ranking explanations",
    )

    # SELECT
    select = subparsers.add_parser(
        "select",
        help="Record a user selection for learning",
    )
    select.add_argument("text", type=str)
    select.add_argument("value", type=str)

    args = parser.parse_args()

    engine = build_engine()

    if args.command == "suggest":
        handle_suggest(
            engine=engine,
            text=args.text,
            explain=args.explain,
        )
    elif args.command == "select":
        handle_select(
            engine=engine,
            text=args.text,
            value=args.value,
        )


def handle_suggest(
    engine: AutocompleteEngine,
    text: str,
    explain: bool,
) -> None:
    suggestions = engine.suggest(text)

    if not explain:
        for suggestion in suggestions:
            print(suggestion.value)
        return

    explanations = engine.explain(text)

    for explanation in explanations:
        print(
            f"{explanation.value:12} "
            f"base={explanation.base_score:.2f} "
            f"+ history={explanation.history_boost:.2f} "
            f"=> {explanation.final_score:.2f}"
        )


def handle_select(
    engine: AutocompleteEngine,
    text: str,
    value: str,
) -> None:
    engine.record_selection(text, value)
    print(f"Recorded selection '{value}' for input '{text}'")
