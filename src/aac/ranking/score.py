from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    """
    Pure score-based ranker.
    No learning or mutation and stable ordering.
    """

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        if not suggestions:
            return []

        # Stable sort by score 
        ordered = sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )

        return [s.suggestion for s in ordered]
