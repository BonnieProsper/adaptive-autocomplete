"""DecayRanker: applies exponential time-decay to selection counts. Recent selections rank higher."""
from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation

# ---------------------------------------------------------------------
# Decay function
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class DecayFunction:
    """
    Time-based exponential decay.

    weight = 0.5 ** (elapsed_seconds / half_life_seconds)
    """
    half_life_seconds: float

    def weight(self, *, now: datetime, event_time: datetime) -> float:
        if event_time.tzinfo is None:
            raise ValueError("History timestamps must be timezone-aware")

        if event_time > now:
            return 1.0

        elapsed = (now - event_time).total_seconds()
        if elapsed <= 0:
            return 1.0

        return float(0.5 ** (elapsed / self.half_life_seconds))


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


# ---------------------------------------------------------------------
# Ranker
# ---------------------------------------------------------------------

class DecayRanker(Ranker, LearnsFromHistory):
    """
    Boosts suggestions using exponentially decayed selection counts.
    Recent selections rank higher; old ones fade out.

    rank() and explain() share one _decayed_counts() call per (prefix, now) pair.
    Cache is thread-local so concurrent rank() calls on a shared engine
    (e.g. with ThreadSafeHistory) don't corrupt each other's state.
    """

    def __init__(
        self,
        history: History,
        decay: DecayFunction,
        *,
        weight: float = 1.0,
        now: datetime | None = None,
    ) -> None:
        self.history = history
        self._decay = decay
        self._weight = weight
        self._now = now

        # Per-thread cache so concurrent rank() calls on a shared engine
        # (e.g. with ThreadSafeHistory) don't corrupt each other's state.
        self._local: threading.local = threading.local()

    def _now_utc(self) -> datetime:
        return self._now if self._now is not None else utcnow()

    def _decayed_counts(self, prefix: str, now: datetime) -> dict[str, float]:
        """Recency-weighted selection counts. Cached per (prefix, now) from the last rank() call."""
        local = self._local
        if (
            getattr(local, "cache_valid", False)
            and prefix == getattr(local, "cached_prefix", None)
            and now == getattr(local, "cached_now", None)
        ):
            return local.cached_counts  # type: ignore[no-any-return]  # threading.local attrs are untyped

        counts: dict[str, float] = defaultdict(float)
        for entry in self.history.entries_for_prefix(prefix):
            counts[entry.value] += self._decay.weight(
                now=now,
                event_time=entry.timestamp,
            )

        result = dict(counts)
        local.cached_prefix = prefix
        local.cached_now = now
        local.cached_counts = result
        local.cache_valid = True
        return result

    def ranker_config(self) -> dict[str, float]:
        """Return parameters needed to reconstruct this ranker."""
        return {
            "half_life_seconds": self._decay.half_life_seconds,
            "weight": self._weight,
        }

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        self._local.cache_valid = False
        now = self._now_utc()
        self._local.rank_now = now
        decayed = self._decayed_counts(prefix, now)
        if not decayed:
            return list(suggestions)

        scored: list[tuple[float, int, ScoredSuggestion]] = []

        for index, s in enumerate(suggestions):
            boost = decayed.get(s.suggestion.value, 0.0) * self._weight
            final_score = s.score + boost

            # Add a trace entry when boost is non-zero so debug() shows
            # DecayRanker's contribution alongside LearningRanker's.
            new_trace = s.trace
            if boost > 0.0:
                new_trace = s.trace + (
                    f"DecayRanker boost={boost:.4f}",
                )

            scored.append((
                final_score,
                index,  # stable tiebreaker: preserve original order on equal scores
                ScoredSuggestion(
                    suggestion=s.suggestion,
                    score=final_score,
                    explanation=s.explanation,
                    trace=new_trace,
                ),
            ))

        scored.sort(key=lambda t: (-t[0], t[1]))
        return [s for _, _, s in scored]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        rank_now = getattr(self._local, "rank_now", None)
        now = rank_now if rank_now is not None else self._now_utc()
        decayed = self._decayed_counts(prefix, now)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            boost = decayed.get(s.suggestion.value, 0.0) * self._weight
            # base_score=0.0: this ranker contributes boost only, not a base score.
            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=0.0,
                    history_boost=boost,
                    final_score=boost,
                    source="decay",
                    base_components={},
                    history_components={"decay": boost} if boost > 0 else {},
                )
            )

        return explanations
