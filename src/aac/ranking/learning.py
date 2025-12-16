from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker


class LearningRanker:
    def __init__(
        self,
        history: History,
        boost: float = 1.0,
    ) -> None:
        self._history = history
        self._boost = boost

    def rank(
        self,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        adjusted: list[ScoredSuggestion] = []

        for scored in suggestions:
            bonus = self._history.get(scored.suggestion.value)
            adjusted_score = scored.score + bonus * self._boost

            adjusted.append(
                ScoredSuggestion(
                    scored.suggestion,
                    adjusted_score,
                )
            )

        adjusted.sort(key=lambda s: s.score, reverse=True)
        return [s.suggestion for s in adjusted]
