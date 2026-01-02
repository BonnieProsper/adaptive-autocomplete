from __future__ import annotations

import math
from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation


class LearningRanker(Ranker, LearnsFromHistory):
    """
    Ranker that adapts suggestion ordering based on user selection history.

    Learning model:
    - Historical counts produce additive score boosts
    - Boosts are bounded to prevent runaway dominance
    - No signal => original order preserved

    Invariants:
    - Pure: does not mutate history or suggestions
    - Stable: preserves order without history
    - Additive: learning never suppresses suggestions
    """

    def __init__(
        self,
        history: History,
        *,
        boost: float = 1.0,
        dominance_ratio: float = 1.0,
    ) -> None:
        if boost < 0.0:
            raise ValueError("boost must be non-negative")

        if dominance_ratio < 0.0:
            raise ValueError("dominance_ratio must be non-negative")

        self._history = history
        self._boost = boost
        self._dominance_ratio = dominance_ratio

    def _decayed_count(self, count: int) -> float:
        """
        Apply exponential decay to a raw count.

        This prevents runaway growth while still
        rewarding repeated selection.
        """
        if count <= 0:
            return 0.0

        # Simple, explainable decay
        return count * math.exp(-0.5 * count)

    def _history_boost(self, *, count: int, base_score: float) -> float:
        """
        Compute a bounded learning boost.

        Bounding strategy:
        - Decayed count signal
        - Global boost weight
        - Relative dominance cap
        """
        if count <= 0:
            return 0.0

        decayed = self._decayed_count(count)
        boost = decayed * self._boost

        # Relative dominance cap
        if base_score > 0.0:
            boost = min(boost, self._dominance_ratio * base_score)

        return boost

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self._history.counts_for_prefix(prefix)

        # Invariant: no signal => preserve order
        if not counts:
            return list(suggestions)

        adjusted: list[tuple[float, int, ScoredSuggestion]] = []

        for idx, s in enumerate(suggestions):
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(
                count=count,
                base_score=s.score,
            )
            adjusted.append((s.score + boost, idx, s))

        # Stable sort: score desc, original order as tie-breaker
        adjusted.sort(key=lambda t: (-t[0], t[1]))

        return [s for _, _, s in adjusted]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        counts = self._history.counts_for_prefix(prefix)

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
