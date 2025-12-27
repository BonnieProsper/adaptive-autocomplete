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
        """
        Record a completion selection.
        """
        self._entries.append(HistoryEntry(prefix, value))

    def entries(self) -> Sequence[HistoryEntry]:
        """
        Immutable view of recorded events.
        """
        return tuple(self._entries)

    def counts_for_prefix(self, prefix: str) -> dict[str, int]:
        """
        Count how often each value was selected for a given prefix.
        """
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix == prefix:
                counts[entry.value] += 1

        return dict(counts)

    def count(self, value: str) -> int:
        """
        Total count for a specific value across all prefixes.
        """
        return sum(
            1 for entry in self._entries
            if entry.value == value
        )

    def snapshot(self) -> dict[str, dict[str, int]]:
        """
        Returns a serializable snapshot of history data.

        Format:
        {
            "<prefix>": {
                "<value>": count
            }
        }
        """
        snapshot: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for entry in self._entries:
            snapshot[entry.prefix][entry.value] += 1

        return {
            prefix: dict(values)
            for prefix, values in snapshot.items()
        }

