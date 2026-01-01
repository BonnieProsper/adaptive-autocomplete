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

    Learning model:
    - Boost = selection_count * weight
    - Linear, monotonic, fully explainable

    Invariants:
    - No history signal => original order preserved
    - Learning is additive (never suppresses)
    - Does not mutate input suggestions
    """

    def __init__(
        self,
        history: History,
        weight: float = 1.0,
        *,
        boost: float | None = None,
    ) -> None:
        """
        Parameters:
        - history: shared selection history (single source of truth)
        - weight: canonical learning strength
        - boost: public alias for weight (API compatibility)
        """
        if boost is not None:
            if weight != 1.0:
                raise ValueError(
                    "Specify only one of 'weight' or 'boost', not both"
                )
            weight = boost

        self.history = history
        self._weight = weight

    def _history_boost(self, count: int) -> float:
        """
        Compute a linear, monotonic learning boost.

        Rationale:
        - Fully explainable
        - Matches public API expectations
        - Easy to extend later (decay, caps, non-linear variants)
        """
        if count <= 0:
            return 0.0
        return count * self._weight

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)
        if not counts:
            return list(suggestions)

        adjusted: list[tuple[float, ScoredSuggestion]] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(count)
            adjusted.append((s.score + boost, s))

        adjusted.sort(key=lambda t: t[0], reverse=True)
        return [s for _, s in adjusted]

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        counts = self.history.counts_for_prefix(prefix)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(count)

            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=boost,
                    final_score=s.score + boost,
                    source="learning",
                )
            )

        return explanations

    def explain_as_dicts(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[dict[str, float | str]]:
        """
        Export ranking explanations in a JSON-safe, stable schema.

        NOTE:
        - Public contract
        - Internal mechanics intentionally excluded
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
