from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion


class ScoreRanker:
    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        sorted_items = sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )
        return [s.suggestion for s in sorted_items]
