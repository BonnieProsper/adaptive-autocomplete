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

    Design principles:
    - Learning is additive and monotonic
    - No history signal => original order preserved
    - Ranking and explanation are derived from the same signal
    - Does not mutate input suggestions
    """

    def __init__(self, history: History, boost: float = 1.0) -> None:
        self._history = history
        self._boost = boost

    def _history_boost(self, prefix: str, value: str) -> float:
        """
        Compute the learning-based boost for a suggestion value.
        """
        counts = self._history.counts_for_prefix(prefix)
        return counts.get(value, 0) * self._boost

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        # Fast path: no history => preserve order
        counts = self._history.counts_for_prefix(prefix)
        if not counts:
            return list(suggestions)

        scored: list[tuple[float, ScoredSuggestion]] = []

        for s in suggestions:
            boost = counts.get(s.suggestion.value, 0) * self._boost
            scored.append((s.score + boost, s))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [s for _, s in scored]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        """
        Produce ranking explanations consistent with learning adjustments.
        """
        explanations: list[RankingExplanation] = []

        for s in suggestions:
            boost = self._history_boost(prefix, s.suggestion.value)

            base = RankingExplanation.from_predictor(
                value=s.suggestion.value,
                score=s.score,
                source="predictor",
            )

            explanations.append(base.apply_history_boost(boost))

        return explanations

    def explain_as_dicts(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[dict[str, float | str]]:
        """
        Export explanations using an explicit public schema.
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
