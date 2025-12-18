from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryEntry:
    """
    A single observed completion event.
    """
    prefix: str
    value: str


class History:
    """
    Append-only store of user completion events.

    Acts as the source of truth for all learning signals.
    """
    def __init__(self) -> None:
        self._entries: list[HistoryEntry] = []

    def record(self, prefix: str, value: str) -> None:
        self._entries.append(HistoryEntry(prefix, value))

    def entries(self) -> Sequence[HistoryEntry]:
        return tuple(self._entries)

    def counts_for_prefix(self, prefix: str) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix == prefix:
                counts[entry.value] += 1

        return dict(counts)

    def count(self, value: str) -> int:
        return sum(
            prefix_counts.get(value, 0)
            for prefix_counts in self._counts.values()
        )


