from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation



# Decay function moved from domain

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
        Uses exponential decay: weight = 0.5 ** (elapsed / half_life)
        """
        if event_time > now:
            return 1.0

        elapsed = (now - event_time).total_seconds()
        if elapsed <= 0:
            return 1.0

        return float(0.5 ** (elapsed / self.half_life_seconds))


def utcnow() -> datetime:
    """Centralized time source (UTC, timezone-aware)."""
    return datetime.now(tz=timezone.utc)


class DecayRanker(Ranker, LearnsFromHistory):
    """
    Ranker that boosts suggestions based on recency-weighted history.

    Learning model:
    - Each historical event contributes a decayed weight
    - Total boost = sum(decayed weights) * weight
    - Fully explainable and bounded

    Intended to be composed with LearningRanker, not to replace it.
    """

    def __init__(
        self,
        history: History,
        decay: DecayFunction,
        *,
        weight: float = 1.0,
        now: datetime | None = None,
    ) -> None:
        """
        Parameters:
        - history: shared selection history
        - decay: decay function (half-life controlled)
        - weight: scaling factor for decay signal
        - now: injected clock for determinism/testing
        """
        self.history = history
        self._decay = decay
        self._weight = weight
        self._now = now

    def _current_time(self) -> datetime:
        return self._now if self._now is not None else utcnow()

    def _decayed_counts(self, prefix: str) -> dict[str, float]:
        """
        Compute time-decayed counts per suggestion value.
        """
        now = self._current_time()
        counts: dict[str, float] = defaultdict(float)

        for entry in self.history.entries():
            if entry.prefix != prefix:
                continue

            w = self._decay.weight(
                now=now,
                event_time=entry.timestamp,
            )
            counts[entry.value] += w

        return dict(counts)

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        decayed = self._decayed_counts(prefix)
        if not decayed:
            return list(suggestions)

        adjusted: list[tuple[float, ScoredSuggestion]] = []

        for s in suggestions:
            boost = decayed.get(s.suggestion.value, 0.0) * self._weight
            adjusted.append((s.score + boost, s))

        adjusted.sort(key=lambda t: t[0], reverse=True)
        return [s for _, s in adjusted]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        decayed = self._decayed_counts(prefix)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            boost = decayed.get(s.suggestion.value, 0.0) * self._weight

            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=boost,
                    final_score=s.score + boost,
                    source="decay",
                )
            )

        return explanations
