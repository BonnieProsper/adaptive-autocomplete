from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )
        return [s.suggestion for s in sorted_suggestions]
