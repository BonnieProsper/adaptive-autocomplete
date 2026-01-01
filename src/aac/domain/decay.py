from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DecayFunction:
    """
    Time-based decay function.

    Converts elapsed time (seconds) into a weight in [0, 1].

    Properties: Monotonic decreasing, deterministic, explainable
    """

    half_life_seconds: float

    def weight(self, *, now: datetime, event_time: datetime) -> float:
        """
        Compute decay weight for an event timestamp.

        Uses exponential decay:
            weight = 0.5 ** (elapsed / half_life)
        """
        if event_time > now:
            return 1.0

        elapsed = (now - event_time).total_seconds()
        if elapsed <= 0:
            return 1.0

        return 0.5 ** (elapsed / self.half_life_seconds)


def utcnow() -> datetime:
    """
    Centralized time source (UTC, timezone-aware).
    """
    return datetime.now(tz=timezone.utc)
