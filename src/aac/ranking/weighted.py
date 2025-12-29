# aac/ranking/weighted.py
from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class WeightedRanker(Ranker):
    """
    Wraps a ranker and scales its output scores by a constant factor.

    Design:
    - Doesn't mutate input suggestions
    - Produces new ScoredSuggestion instances
    - Preserves ordering and explanations
    """

    def __init__(self, ranker: Ranker, weight: float = 1.0) -> None:
        if weight <= 0:
            raise ValueError("weight must be positive")
        self._ranker = ranker
        self._weight = weight

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        ranked = self._ranker.rank(prefix, suggestions)

        if self._weight == 1.0:
            return list(ranked)

        return [
            ScoredSuggestion(
                suggestion=s.suggestion,
                score=s.score * self._weight,
                explanation=s.explanation,
                trace=list(s.trace),
            )
            for s in ranked
        ]

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
