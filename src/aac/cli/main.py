# TODO Extend later, add pipelines etc
from __future__ import annotations

import argparse
from pathlib import Path

from aac.domain.history import History
from aac.engine.engine import AutocompleteEngine
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.ranking.learning import LearningRanker
from aac.storage.json_store import JsonHistoryStore

DEFAULT_HISTORY_PATH = Path(".aac_history.json")
DEFAULT_LIMIT = 10


def build_engine(history: History) -> AutocompleteEngine:
    """
    Construct the autocomplete engine.

    This function is intentionally explicit:
    - predictable behavior
    - testable construction
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
        description="Adaptive autocomplete engine with learning and explainability",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # suggest
    suggest = subparsers.add_parser(
        "suggest",
        help="Generate autocomplete suggestions",
    )
    suggest.add_argument("text", type=str)
    suggest.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of suggestions to display",
    )
    suggest.add_argument(
        "--explain",
        action="store_true",
        help="Show scoring explanations instead of plain suggestions",
    )

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
        handle_suggest(
            engine=engine,
            text=args.text,
            limit=args.limit,
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
    limit: int,
    explain: bool,
) -> None:
    if explain:
        explanations = engine.explain(text)[:limit]
        for exp in explanations:
            print(
                f"{exp.value:12} "
                f"base={exp.base_score:.2f} "
                f"+ history={exp.history_boost:.2f} "
                f"=> {exp.final_score:.2f}"
            )
        return

    suggestions = engine.suggest(text)[:limit]
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
