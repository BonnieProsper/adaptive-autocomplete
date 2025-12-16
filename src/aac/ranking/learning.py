from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion


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
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        counts = self._history.counts_for_prefix(prefix)

        adjusted: list[ScoredSuggestion] = []

        for scored in suggestions:
            bonus = counts.get(scored.suggestion.value, 0)
            adjusted_score = scored.score + bonus * self._boost

            adjusted.append(
                ScoredSuggestion(
                    scored.suggestion,
                    adjusted_score,
                )
            )

        adjusted.sort(key=lambda s: s.score, reverse=True)
        return [s.suggestion for s in adjusted]
