from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory


class LearningRanker(Ranker, LearnsFromHistory):
    """
    Ranker that adapts suggestion ordering based on user selection history.

    Learning is additive:
    - Suggestions with no history remain neutral
    - Ordering is stable when no learning signal exists
    """

    def __init__(self, history: History, boost: float = 1.0) -> None:
        self._history = history
        self._boost = boost

    @property
    def history(self) -> History:
        return self._history

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        # No suggestions = nothing to rank
        if not suggestions:
            return []

        counts = self._history.counts_for_prefix(prefix)

        # fast method: no learning signal = preserve original order
        if not counts:
            return [s.suggestion for s in suggestions]

        adjusted: list[ScoredSuggestion] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)

            # Only adjust score if learning exists
            if count > 0:
                adjusted.append(
                    ScoredSuggestion(
                        suggestion=s.suggestion,
                        score=s.score + count * self._boost,
                    )
                )
            else:
                adjusted.append(s)

        # Stable sort: only score determines reordering
        adjusted.sort(key=lambda s: s.score, reverse=True)

        return [s.suggestion for s in adjusted]
