from __future__ import annotations

import argparse
from pathlib import Path

from aac.cli import debug, explain, record, suggest
from aac.cli.app import build_engine
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
        default="developer",
        help="Autocomplete engine preset",
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

    store = JsonHistoryStore(DEFAULT_HISTORY_PATH)
    history = store.load()

    engine = build_engine(
        history=history,
        preset=args.preset,
    )

    if args.command == "suggest":
        suggest.run(engine=engine, text=args.text, limit=args.limit)
    elif args.command == "explain":
        explain.run(engine=engine, text=args.text, limit=args.limit)
    elif args.command == "record":
        record.run(engine=engine, store=store, text=args.text, value=args.value)
    elif args.command == "debug":
        debug.run(engine=engine, text=args.text)
