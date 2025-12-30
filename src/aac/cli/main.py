from __future__ import annotations

import argparse
from pathlib import Path

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker
from aac.storage.json_store import JsonHistoryStore

DEFAULT_HISTORY_PATH = Path(".aac_history.json")


def build_engine(
    history: History,
) -> AutocompleteEngine:
    """
    Build the autocomplete engine.

    Kept pure and explicit so:
    - it is testable
    - persistence is handled outside
    - behavior matches production usage
    """
    return AutocompleteEngine(
        predictors=[
            StaticPrefixPredictor(
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

    # PERSISTENCE
    store = JsonHistoryStore(DEFAULT_HISTORY_PATH)
    history = store.load()
    engine = build_engine(history)

    if args.command == "suggest":
        handle_suggest(
            engine=engine,
            text=args.text,
            explain=args.explain,
        )

    elif args.command == "select":
        handle_select(
            engine=engine,
            store=store,
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
    store: JsonHistoryStore,
    text: str,
    value: str,
) -> None:
    engine.record_selection(text, value)
    store.save(engine.history)
    print(f"Recorded selection '{value}' for input '{text}'")
