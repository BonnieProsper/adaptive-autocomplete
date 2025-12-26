from __future__ import annotations

import json
from pathlib import Path

from aac.domain.history import History


class JsonHistory(History):
    """
    File-backed History implementation.

    - Loads on startup
    - Writes on each update
    - Format is stable and human-readable
    """

    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return

        data = json.loads(self._path.read_text())

        for prefix, values in data.items():
            for value, count in values.items():
                for _ in range(count):
                    super().record(prefix, value)

    def record(self, prefix: str, value: str) -> None:
        super().record(prefix, value)
        self._save()

    def _save(self) -> None:
        data: dict[str, dict[str, int]] = {}

        for prefix, counter in self._history.items():
            data[prefix] = dict(counter)

        self._path.write_text(json.dumps(data, indent=2))
