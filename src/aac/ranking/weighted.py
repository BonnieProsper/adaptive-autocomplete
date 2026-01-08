from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class WeightedRanker(Ranker):
    """
    Wraps a ranker and scales its explanatory contribution.

    - Does NOT modify ScoredSuggestion instances
    - Does NOT change ordering semantics
    - Only affects explanation math

    This preserves engine invariants:
    - identity stability
    - deterministic ordering
    - explanation consistency
    """

    def __init__(self, ranker: Ranker, weight: float = 1.0) -> None:
        if weight <= 0.0:
            raise ValueError("weight must be positive")
        self._ranker = ranker
        self._weight = weight

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        # Delegate ordering entirely
        return list(self._ranker.rank(prefix, suggestions))

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        explanations = self._ranker.explain(prefix, suggestions)

        if self._weight == 1.0:
            return explanations

        return [
            RankingExplanation(
                value=e.value,
                base_score=e.base_score * self._weight,
                history_boost=e.history_boost * self._weight,
                final_score=e.final_score * self._weight,
                source=e.source,
            )
            for e in explanations
        ]
