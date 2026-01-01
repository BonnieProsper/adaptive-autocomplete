# TODO Extend later, make better
from __future__ import annotations

import argparse
from pathlib import Path

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker
from aac.storage.json_store import JsonHistoryStore

DEFAULT_HISTORY_PATH = Path(".aac_history.json")


def build_engine(history: History) -> AutocompleteEngine:
    """
    Build the autocomplete engine.

    Kept explicit and pure so:
    - behavior is deterministic
    - tests are simple
    - pipelines can replace this later
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
        description="Adaptive autocomplete engine with learning",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # suggest
    suggest = subparsers.add_parser(
        "suggest",
        help="Generate autocomplete suggestions",
    )
    suggest.add_argument("text", type=str)

    # select
    select = subparsers.add_parser(
        "select",
        help="Record a user selection for learning",
    )
    select.add_argument("text", type=str)
    select.add_argument("value", type=str)

    args = parser.parse_args()

    # persistence
    store = JsonHistoryStore(DEFAULT_HISTORY_PATH)
    history = store.load()

    engine = build_engine(history)

    if args.command == "suggest":
        handle_suggest(engine, args.text)

    elif args.command == "select":
        handle_select(engine, store, args.text, args.value)


def handle_suggest(
    engine: AutocompleteEngine,
    text: str,
) -> None:
    suggestions = engine.suggest(text)

    for suggestion in suggestions:
        print(suggestion.value)


def handle_select(
    engine: AutocompleteEngine,
    store: JsonHistoryStore,
    text: str,
    value: str,
) -> None:
    engine.record_selection(text, value)
    store.save(engine.history)
    print(f"Recorded selection '{value}' for input '{text}'")
