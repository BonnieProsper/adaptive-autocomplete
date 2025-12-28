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
    - No history signal = original order preserved
    - Learning is additive & monotonic
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

        if not counts:
            return list(suggestions)

        adjusted: list[tuple[float, ScoredSuggestion]] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            score = s.score + count * self._boost
            adjusted.append((score, s))

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
            history_boost = count * self._boost

            explanations.append(
                RankingExplanation(
                    value=s.suggestion.value,
                    base_score=s.score,
                    history_boost=history_boost,
                    final_score=s.score + history_boost,
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
        Export ranking explanations in a JSON-safe structure.

        This is the serialization boundary — callers should not
        depend on RankingExplanation internals.
        """
        return [
            {
                "value": e.value,
                "base_score": e.base_score,
                "history_boost": e.history_boost,
                "final_score": e.final_score,
                "source": e.source,
            }
            for e in self.explain(prefix, suggestions)
        ]
