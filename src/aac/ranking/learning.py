from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation


class LearningRanker(Ranker, LearnsFromHistory):
    """
    Ranker that adapts suggestion ordering based on user selection history.

    Learning is additive and stable:
    - No history → original order preserved
    - More frequent selections → higher rank
    """

    def __init__(self, history: History, boost: float = 1.0) -> None:
        self.history = history
        self._boost = boost

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)

        # No learning signal → preserve original order
        if not counts:
            return [s.suggestion for s in suggestions]

        adjusted: list[ScoredSuggestion] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)

            if count > 0:
                adjusted.append(
                    ScoredSuggestion(
                        suggestion=s.suggestion,
                        score=s.score + count * self._boost,
                    )
                )
            else:
                adjusted.append(s)

        # Stable sort by score (Python sort is stable)
        adjusted.sort(key=lambda s: s.score, reverse=True)

        return [s.suggestion for s in adjusted]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        """
        Produce explanations for how each suggestion's score is derived.
        Does not mutate history or affect ranking.
        """
        counts = self.history.counts_for_prefix(prefix)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            history_boost = count * self._boost
            final_score = s.score + history_boost

            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=history_boost,
                    final_score=final_score,
                )
            )

        # Sorted for readability, not required by rank()
        explanations.sort(key=lambda e: e.final_score, reverse=True)

        return explanations

