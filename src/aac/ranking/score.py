from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    """Ranks suggestions by descending score."""

    def rank(
        self, suggestions: Sequence[ScoredSuggestion]
    ) -> list[Suggestion]:
        ordered = sorted(suggestions, key=lambda s: s.score, reverse=True)
        return [s.suggestion for s in ordered]
