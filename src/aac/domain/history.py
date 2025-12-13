from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True)
class HistoryEntry:
    """
    A single observed completion event.
    """
    context: str
    chosen: str


@dataclass(frozen=True)
class HistoryWindow:
    """
    A read-only window over recent history.
    """
    entries: Sequence[HistoryEntry]

    def last_n(self, n: int) -> Sequence[HistoryEntry]:
        return self.entries[-n:]

