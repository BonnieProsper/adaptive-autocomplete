from __future__ import annotations

from typing import Iterable, List

from aac.domain.types import ScoredSuggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    def rank(
        self,
        prefix: str,
        suggestions: Iterable[ScoredSuggestion],
    ) -> List[ScoredSuggestion]:
        # Defensive copy to preserve idempotence
        ordered = sorted(
            suggestions,
            key=lambda s: s.score,
            reverse=True,
        )
        return list(ordered)


def score_and_rank(
    suggestions: Iterable[ScoredSuggestion],
) -> List[ScoredSuggestion]:
    """
    Rank suggestions purely by their existing scores.
    """
    return ScoreRanker().rank("", suggestions)
