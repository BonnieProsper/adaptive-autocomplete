from __future__ import annotations

import argparse
from pathlib import Path

from aac import engine
from aac.cli import debug, explain, record, suggest
from aac.domain import history
from aac.cli.app import build_engine
from aac.engine import engine
from aac.presets import available_presets
from aac.storage.json_store import JsonHistoryStore

DEFAULT_HISTORY_PATH = Path(".aac_history.json")
DEFAULT_LIMIT = 10


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aac",
        description="Adaptive autocomplete engine with learning and explainability",
    )

    parser.add_argument(
        "--preset",
        default=available_presets()[0],
        choices=available_presets(),
        help="Autocomplete engine preset",
    )

    parser.add_argument(
        "--history-path",
        type=Path,
        default=DEFAULT_HISTORY_PATH,
        help="Path to persisted autocomplete history",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    suggest_p = subparsers.add_parser("suggest")
    suggest_p.add_argument("text")
    suggest_p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)

    explain_p = subparsers.add_parser("explain")
    explain_p.add_argument("text")
    explain_p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)

    record_p = subparsers.add_parser("record")
    record_p.add_argument("text")
    record_p.add_argument("value")

    debug_p = subparsers.add_parser("debug")
    debug_p.add_argument("text")

    args = parser.parse_args()

    store = JsonHistoryStore(args.history_path)
    history = store.load()

    engine = build_engine(
    preset=args.preset,
    )

    # hydrate engine history from store
    engine.history.replace(history)

    dispatch = {
        "suggest": lambda: suggest.run(
            engine=engine,
            text=args.text,
            limit=args.limit,
        ),
        "explain": lambda: explain.run(
            engine=engine,
            text=args.text,
            limit=args.limit,
        ),
        "record": lambda: record.run(
            engine=engine,
            store=store,
            text=args.text,
            value=args.value,
        ),
        "debug": lambda: debug.run(
            engine=engine,
            text=args.text,
        ),
    }

    dispatch[args.command]()
