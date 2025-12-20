from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    """
    Baseline ranker.
    Preserves original predictor ordering and scores.
    """

    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        # No-op ranking: preserve order and metadata
        return list(suggestions)
