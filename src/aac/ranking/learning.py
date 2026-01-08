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

    Invariants:
    - No history signal => original order preserved
    - Learning is additive (never suppresses)
    - Learning influence is bounded
    - Deterministic and stable
    - Does not mutate inputs or history
    """

    def __init__(
        self,
        history: History,
        *,
        boost: float = 1.0,
        dominance_ratio: float = 1.0,
        config: object | None = None,  # forward compatibility
    ) -> None:
        if boost < 0.0:
            raise ValueError("boost must be non-negative")

        if dominance_ratio < 0.0:
            raise ValueError("dominance_ratio must be non-negative")

        # Required by LearnsFromHistory
        self.history: History = history

        self._boost = boost
        self._dominance_ratio = dominance_ratio

        # config intentionally unused

    # --- learning internals ---

    def _compute_history_boost(self, *, count: int, base_score: float) -> float:
        """
        Compute a bounded linear learning boost.

        raw_boost = count * boost
        raw_boost <= dominance_ratio * base_score
        """
        if count <= 0:
            return 0.0

        boost = count * self._boost

        if base_score > 0.0:
            boost = min(boost, self._dominance_ratio * base_score)

        return boost

    def _compute_adjusted_score(
        self,
        *,
        value: str,
        base_score: float,
        counts: dict[str, int],
    ) -> float:
        count = counts.get(value, 0)
        boost = self._compute_history_boost(
            count=count,
            base_score=base_score,
        )
        return base_score + boost

    # --- ranking ---

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        if not suggestions:
            return []

        counts = self.history.counts_for_prefix(prefix)

        # Invariant: no history signal => preserve original order
        if not counts:
            return list(suggestions)

        scored: list[tuple[float, int, ScoredSuggestion]] = []

        for index, suggestion in enumerate(suggestions):
            final_score = self._compute_adjusted_score(
                value=suggestion.suggestion.value,
                base_score=suggestion.score,
                counts=counts,
            )
            scored.append((final_score, index, suggestion))

        # Stable: score desc, original index as tiebreaker
        scored.sort(key=lambda t: (-t[0], t[1]))

        return [suggestion for _, _, suggestion in scored]

    # --- explanation ---

    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        ranked = self.rank(prefix, suggestions)
        counts = self.history.counts_for_prefix(prefix)

        explanations: list[RankingExplanation] = []

        for s in ranked:
            count = counts.get(s.suggestion.value, 0)
            boost = self._compute_history_boost(
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
