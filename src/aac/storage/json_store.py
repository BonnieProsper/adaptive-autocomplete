from __future__ import annotations

import json
from pathlib import Path

from aac.domain.history import History
from aac.storage.base import HistoryStore


class JsonHistoryStore(HistoryStore):
    """
    JSON-backed persistence for History.

    Responsibilities:
        - Load persisted history into domain model
        - Save explicit, JSON-serializable snapshots
        - Defensively handle legacy or corrupted data

    Design notes:
        - Domain objects remain I/O-free
        - Storage layer performs data sanitization
        - Backwards-compatible with older snapshots
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> History:
        """
        Load history from disk.

        Returns:
            History populated from storage, or empty History
            if no file exists.

        Notes:
            - Coerces all keys to strings to guard against
              legacy snapshots containing non-string keys.
            - Ignores malformed entries instead of failing.
        """
        history = History()

        if not self._path.exists():
            return history

        data = json.loads(self._path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            return history

        for prefix, values in data.items():
            prefix_str = str(prefix)

            if not isinstance(values, dict):
                continue

            for value, count in values.items():
                value_str = str(value)

                try:
                    count_int = int(count)
                except (TypeError, ValueError):
                    continue

                for _ in range(count_int):
                    history.record(prefix_str, value_str)

        return history

    def save(self, history: History) -> None:
        """
        Persist history snapshot to disk.

        Assumes History.snapshot() returns a fully
        JSON-serializable structure.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)

        snapshot = history.snapshot()

        self._path.write_text(
            json.dumps(snapshot, indent=2, sort_keys=True),
            encoding="utf-8",
        )

