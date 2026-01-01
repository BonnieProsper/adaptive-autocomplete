from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class HistoryEntry:
    """
    A single observed completion event.

    Notes:
    - Timestamp is immutable and always timezone-aware (UTC).
    - Enables recency-aware learning signals (decay, sessions, trends).
    """
    prefix: str
    value: str
    timestamp: datetime


class History:
    """
    Append-only store of user completion events.

    Acts as the single source of truth for all learning signals.

    Design guarantees:
    - Entries are immutable once recorded
    - No deletion or mutation
    - Backwards-compatible counting APIs
    """

    def __init__(self) -> None:
        self._entries: list[HistoryEntry] = []

    def record(
        self,
        prefix: str,
        value: str,
        *,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Record a completion selection.

        Parameters:
        - prefix: user input prefix
        - value: selected completion
        - timestamp: optional explicit timestamp (UTC recommended)

        If timestamp is omitted, current UTC time is used.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        self._entries.append(
            HistoryEntry(
                prefix=prefix,
                value=value,
                timestamp=timestamp,
            )
        )

    def entries(self) -> Sequence[HistoryEntry]:
        """
        Immutable view of all recorded events.
        """
        return tuple(self._entries)

    def entries_for_prefix(self, prefix: str) -> Sequence[HistoryEntry]:
        """
        All history entries matching a given prefix.
        """
        return tuple(
            entry for entry in self._entries
            if entry.prefix == prefix
        )

    def counts_for_prefix(self, prefix: str) -> dict[str, int]:
        """
        Count how often each value was selected for a given prefix.

        Backwards-compatible API (time-agnostic).
        """
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix == prefix:
                counts[entry.value] += 1

        return dict(counts)

    def counts_for_prefix_since(
        self,
        prefix: str,
        since: datetime,
    ) -> dict[str, int]:
        """
        Count selections for a prefix occurring at or after a timestamp.

        Enables time-decayed or recency-weighted learning.
        """
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix != prefix:
                continue
            if entry.timestamp < since:
                continue
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

        Note:
        - Snapshot intentionally omits timestamps
        - Stable, compact, and storage-friendly
        """
        snapshot: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for entry in self._entries:
            snapshot[entry.prefix][entry.value] += 1

        return {
            prefix: dict(values)
            for prefix, values in snapshot.items()
        }
