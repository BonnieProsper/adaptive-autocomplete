from __future__ import annotations

from collections.abc import Sequence

from aac.domain.types import Prediction, Suggestion
from aac.ranking.base import Ranker


class ScoreRanker(Ranker):
    """Ranks predictions by descending score."""

    def rank(self, predictions: Sequence[Prediction]) -> list[Suggestion]:
        ordered = sorted(predictions, key=lambda p: p.score, reverse=True)
        return [p.suggestion for p in ordered]
