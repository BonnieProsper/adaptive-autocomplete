from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class HistoryEntry:
    """
    A single observed completion event.

    Attributes:
        prefix: The user input prefix at the time of selection.
        value: The completion value selected by the user.
        timestamp: When the selection occurred (UTC, timezone-aware).

    Notes:
        - Entries are immutable once created.
        - Timestamps are always stored in UTC.
        - Enables future extensions such as recency decay, session analysis,
          or time-windowed learning strategies.
    """
    prefix: str
    value: str
    timestamp: datetime


class History:
    """
    Append-only store of user completion events.

    Acts as the single source of truth for all learning signals in the system.

    Design guarantees:
        - Entries are immutable once recorded
        - No deletion or in-place mutation
        - Safe to share across predictors and rankers
        - Persistence-friendly via explicit snapshot export

    This class intentionally separates:
        - In-memory domain representation (HistoryEntry)
        - Serialized representation (snapshot)
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
            prefix: The user input prefix.
            value: The completion selected by the user.
            timestamp: Optional explicit timestamp. If omitted,
                       the current UTC time is used.

        Notes:
            - This operation is append-only.
            - Callers should treat History as write-once per event.
            - Prefix and value are coerced to strings to enforce
              persistence and serialization invariants.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Defensive boundary: History guarantees string keys
        prefix_str = str(prefix)
        value_str = str(value)

        self._entries.append(
            HistoryEntry(
                prefix=prefix_str,
                value=value_str,
                timestamp=timestamp,
            )
        )

    def entries(self) -> Sequence[HistoryEntry]:
        """
        Immutable view of all recorded history entries.

        Returns:
            A tuple of HistoryEntry objects in insertion order.
        """
        return tuple(self._entries)

    def entries_for_prefix(self, prefix: str) -> Sequence[HistoryEntry]:
        """
        Return all history entries matching a given prefix.

        Parameters:
            prefix: The prefix to filter by.

        Returns:
            A tuple of HistoryEntry objects.
        """
        prefix_str = str(prefix)

        return tuple(
            entry for entry in self._entries
            if entry.prefix == prefix_str
        )

    def counts_for_prefix(self, prefix: str) -> dict[str, int]:
        """
        Count how often each value was selected for a given prefix.

        This is a backwards-compatible, time-agnostic API intended
        for simple learning strategies.

        Parameters:
            prefix: The prefix to aggregate counts for.

        Returns:
            Mapping of completion value -> selection count.
        """
        prefix_str = str(prefix)
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix == prefix_str:
                counts[entry.value] += 1

        return dict(counts)

    def counts_for_prefix_since(
        self,
        prefix: str,
        since: datetime,
    ) -> dict[str, int]:
        """
        Count selections for a prefix occurring at or after a timestamp.

        Enables recency-aware or time-decayed learning strategies.

        Parameters:
            prefix: The prefix to aggregate counts for.
            since: Lower bound (inclusive) for entry timestamps.

        Returns:
            Mapping of completion value -> selection count.
        """
        prefix_str = str(prefix)
        counts: dict[str, int] = defaultdict(int)

        for entry in self._entries:
            if entry.prefix != prefix_str:
                continue
            if entry.timestamp < since:
                continue
            counts[entry.value] += 1

        return dict(counts)

    def count(self, value: str) -> int:
        """
        Total count for a specific value across all prefixes.

        Parameters:
            value: Completion value to count.

        Returns:
            Number of times the value was selected.
        """
        value_str = str(value)

        return sum(
            1 for entry in self._entries
            if entry.value == value_str
        )

    def snapshot(self) -> dict[str, dict[str, int]]:
        """
        Return a JSON-serializable snapshot of history data.

        Format:
            {
                "<prefix>": {
                    "<value>": count
                }
            }

        Design notes:
            - Snapshot intentionally omits timestamps
            - Keys and values are JSON primitives only
            - Stable, compact, and storage-friendly
            - Suitable for persistence, debugging, and inspection
        """
        snapshot: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for entry in self._entries:
            snapshot[entry.prefix][entry.value] += 1

        return {
            prefix: dict(values)
            for prefix, values in snapshot.items()
        }
    
    def replace(self, other: "History") -> None:
        """
        Replace contents with another History instance.
        """
        self._entries.clear()
        self._entries.extend(other._entries)

