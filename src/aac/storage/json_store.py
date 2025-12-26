from __future__ import annotations

import json
from pathlib import Path

from aac.domain.history import History
from aac.storage.base import HistoryStore


class JsonHistoryStore(HistoryStore):
    """
    Stores History as JSON on disk.
    """

    def __init__(self, path: Path):
        self._path = path

    def load(self) -> History:
        if not self._path.exists():
            return History()

        data = json.loads(self._path.read_text())
        history = History()

        for text, values in data.items():
            for value, count in values.items():
                history.increment(text, value, count)

        return history

    def save(self, history: History) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(history.snapshot(), indent=2, sort_keys=True)
        )
