from __future__ import annotations

import json
from pathlib import Path

from aac.domain.history import History
from aac.storage.base import HistoryStore


class JsonHistoryStore(HistoryStore):
    """
    JSON-backed persistence for History.

    - Loads History at startup
    - Saves explicit snapshots on demand
    - Keeps domain logic free of I/O
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> History:
        """
        Load history from disk.

        Returns an empty History if no file exists.
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
        self._path.parent.mkdir(parents=True, exist_ok=True)

        self._path.write_text(
            json.dumps(history.snapshot(), indent=2, sort_keys=True)
        )

