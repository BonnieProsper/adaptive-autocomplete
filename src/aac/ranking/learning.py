from __future__ import annotations

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import RankingStrategy


class LearningRanker(RankingStrategy):
    """
    Boosts suggestions based on historical user selections
    for a given prefix.
    """

    def __init__(self, history: History, weight: float = 1.0) -> None:
        self._history = history
        self._weight = weight

    def rank(
        self,
        prefix: str,
        suggestions: list[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        counts = self._history.counts_for_prefix(prefix)

        if not counts:
            return suggestions

        ranked: list[ScoredSuggestion] = []

        for suggestion in suggestions:
            boost = counts.get(suggestion.value, 0) * self._weight
            ranked.append(
                ScoredSuggestion(
                    value=suggestion.value,
                    score=suggestion.score + boost,
                )
            )

        return ranked
