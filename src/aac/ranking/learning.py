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
    - Linear boost: count * boost
    - Optional dominance bounding to prevent runaway effects

    This ranker is intentionally simple, deterministic, and fully explainable.
    More advanced time-based or non-linear learning is handled by DecayRanker.

    Invariants:
    - No history signal => original order preserved
    - Learning is additive (never suppresses)
    - Learning influence is bounded
    - Does not mutate input suggestions or history
    """

    def __init__(
        self,
        history: History,
        *,
        boost: float = 1.0,
        dominance_ratio: float = 1.0,
        config: object | None = None,  # accepted for forward compatibility
    ) -> None:
        if boost < 0.0:
            raise ValueError("boost must be non-negative")

        if dominance_ratio < 0.0:
            raise ValueError("dominance_ratio must be non-negative")

        # Required by LearnsFromHistory: must be a public attribute
        self.history: History = history

        self._boost = boost
        self._dominance_ratio = dominance_ratio

        # config intentionally unused (future extension point)

    # --- learning internals ---

    def _history_boost(self, *, count: int, base_score: float) -> float:
        """
        Compute a bounded linear learning boost.

        Formula:
            boost = count * self._boost

        Bounding:
        - Relative dominance cap based on base score
        """
        if count <= 0:
            return 0.0

        boost = count * self._boost

        if base_score > 0.0:
            boost = min(boost, self._dominance_ratio * base_score)

        return boost

    # --- ranking ---

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)

        # Invariant: no signal => preserve original order
        if not counts:
            return list(suggestions)

        adjusted: list[tuple[float, int, ScoredSuggestion]] = []

        for idx, s in enumerate(suggestions):
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(
                count=count,
                base_score=s.score,
            )
            adjusted.append((s.score + boost, idx, s))

        # Stable sort: score desc, original order as tie-break
        adjusted.sort(key=lambda t: (-t[0], t[1]))

        return [s for _, _, s in adjusted]

    # --- explanation ---

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        counts = self.history.counts_for_prefix(prefix)

        explanations: list[RankingExplanation] = []

        for s in suggestions:
            count = counts.get(s.suggestion.value, 0)
            boost = self._history_boost(
                count=count,
                base_score=s.score,
            )

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
        Export ranking explanations in a JSON-safe schema.
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
