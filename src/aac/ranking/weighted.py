# aac/ranking/weighted.py
from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.explanation import RankingExplanation


class WeightedRanker(Ranker):
    """
    Wraps a ranker with a weight.
    All ranking scores are scaled accordingly.
    """
    def __init__(self, ranker: Ranker, weight: float = 1.0) -> None:
        self.ranker = ranker
        self.weight = weight

    def rank(
        self, prefix: str, suggestions: Sequence[ScoredSuggestion]
    ) -> list[ScoredSuggestion]:
        ranked = self.ranker.rank(prefix, suggestions)
        if self.weight != 1.0:
            for s in ranked:
                s.score *= self.weight
        return ranked

    def explain(
        self, prefix: str, suggestions: Sequence[ScoredSuggestion]
    ) -> list[RankingExplanation]:
        explanations = self.ranker.explain(prefix, suggestions)
        if self.weight != 1.0:
            return [
                RankingExplanation(
                    value=e.value,
                    base_score=e.base_score * self.weight,
                    history_boost=e.history_boost * self.weight,
                    final_score=e.final_score * self.weight,
                    source=e.source,
                )
                for e in explanations
            ]
        return explanations
