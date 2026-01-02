from __future__ import annotations

import math
from collections.abc import Sequence

from aac.config import EngineConfig
from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation


class LearningRanker(Ranker, LearnsFromHistory):
    """
    Ranker that adapts suggestion ordering based on user selection history.

    Learning model:
    - Historical counts are exponentially decayed
    - Learning is gated by a minimum sample threshold
    - Boost is bounded (absolute + relative dominance)

    Invariants:
    - No history signal => original order preserved
    - Learning is additive (never suppresses)
    - Learning influence is bounded
    - Does not mutate input suggestions
    """

    def __init__(
        self,
        history: History,
        *,
        boost: float = 1.0,
        dominance_ratio: float = 1.0,
    ) -> None:
        if max_boost is not None and max_boost < 0.0:
            raise ValueError("max_boost must be non-negative")

        if dominance_ratio < 0.0:
            raise ValueError("dominance_ratio must be non-negative")

        self.history = history
        self._config = config
        self._boost = max_boost
        self._dominance_ratio = dominance_ratio

    def _decayed_count(self, count: int) -> float:
        """
        Apply exponential decay to a raw count.

        Decay formula:
            decayed = count * exp(-decay_rate * count)

        This:
        - rewards recent repetition
        - prevents runaway growth
        """
        if count <= 0:
            return 0.0

        return count * math.exp(
            -self._config.decay_rate * count
        )

    def _history_boost(self, *, count: int, base_score: float) -> float:
        """
        Compute a bounded learning boost.

        Bounding strategy:
        - Minimum sample gate
        - Decayed linear signal
        - Global history weight
        - Optional absolute cap
        - Relative dominance cap
        """
        if count < self._config.min_samples:
            return 0.0

        decayed = self._decayed_count(count)
        boost = decayed * self._config.history_weight

        # Absolute cap
        if self._max_boost is not None:
            boost = min(boost, self._max_boost)

        # Relative dominance cap
        if base_score > 0.0:
            boost = min(
                boost,
                self._dominance_ratio * base_score,
            )

        return boost

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)
        if not counts:
            return list(suggestions)

        adjusted: list[tuple[float, ScoredSuggestion]] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(
                count=count,
                base_score=s.score,
            )
            adjusted.append((s.score + boost, s))

        adjusted.sort(key=lambda t: t[0], reverse=True)
        return [s for _, s in adjusted]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        counts = self.history.counts_for_prefix(prefix)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(
                count=count,
                base_score=s.score,
            )

            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=boost,
                    final_score=s.score + boost,
                    source="learning",
                )
            )

        return explanations

    def explain_as_dicts(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[dict[str, float | str]]:
        """
        Export ranking explanations in a JSON-safe schema.
        """
        return [
            {
                "value": e.value,
                "base_score": e.base_score,
                "history_boost": e.history_boost,
                "final_score": e.final_score,
            }
            for e in self.explain(prefix, suggestions)
        ]
