from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation


class LearningRanker(Ranker, LearnsFromHistory):
    """
    Ranker that adapts suggestion ordering based on user selection history.

    Invariants:
    - No history signal → original order preserved
    - Learning is additive and monotonic
    - Does not mutate input suggestions
    """

    def __init__(self, history: History, boost: float = 1.0) -> None:
        self.history = history
        self._boost = boost

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)

        # No learning signal = preserve order
        if not counts:
            return list(suggestions)

        adjusted: list[ScoredSuggestion] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            history_boost = count * self._boost
            final_score = s.score + history_boost

            adjusted.append(
                ScoredSuggestion(
                    suggestion=s.suggestion,
                    score=final_score,
                    explanation=RankingExplanation(
                        value=s.suggestion.value,
                        base_score=s.score,
                        history_boost=history_boost,
                        final_score=final_score,
                        source="learning",
                    ),
                )
            )

        adjusted.sort(key=lambda s: s.score, reverse=True)
        return adjusted
