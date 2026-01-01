from __future__ import annotations

import argparse
from pathlib import Path

from aac.engine.engine import AutocompleteEngine
from aac.pipelines.developer import build_developer_pipeline
from aac.storage.json_store import JsonHistoryStore

DEFAULT_HISTORY_PATH = Path(".aac_history.json")


PIPELINES = {
    "developer": build_developer_pipeline,
}


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
        "--pipeline",
        choices=PIPELINES.keys(),
        default="developer",
        help="Pipeline to use",
    )
    suggest.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of suggestions",
    )

    # SELECT
    select = subparsers.add_parser(
        "select",
        help="Record a user selection for learning",
    )
    select.add_argument("text", type=str)
    select.add_argument("value", type=str)
    select.add_argument(
        "--pipeline",
        choices=PIPELINES.keys(),
        default="developer",
        help="Pipeline to use",
    )

    args = parser.parse_args()

    # Persistence
    store = JsonHistoryStore(DEFAULT_HISTORY_PATH)
    history = store.load()

    # Pipeline selection
    pipeline_builder = PIPELINES[args.pipeline]
    engine: AutocompleteEngine = pipeline_builder(history)

    if args.command == "suggest":
        handle_suggest(
            engine=engine,
            text=args.text,
            limit=args.limit,
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
) -> None:
    results = engine.suggest(text, limit=limit)

    for idx, suggestion in enumerate(results, start=1):
        print(
            f"{idx:2d}. "
            f"{suggestion.value:20} "
            f"score={suggestion.score:.2f} "
            f"source={suggestion.explanation.source}"
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
