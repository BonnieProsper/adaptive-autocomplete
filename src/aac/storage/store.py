# history/store.py

from __future__ import annotations

import json
from pathlib import Path

from .history import History


class HistoryStore:
    """
    Persistence boundary for History.

    Responsible only for serialization and I/O.
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> History:
        """
        Load history from disk.

        If no history exists, returns an empty History.
        """
        history = History()

        if not self._path.exists():
            return history

        data = json.loads(self._path.read_text())

        for prefix, values in data.items():
            for value, count in values.items():
                for _ in range(count):
                    history.record(prefix, value)

        return history

    def save(self, history: History) -> None:
        """
        Persist history snapshot to disk.
        """
        snapshot = history.snapshot()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(snapshot, indent=2))
