from __future__ import annotations

from collections.abc import Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.score import ScoreRanker


class AutocompleteEngine:
    def __init__(
        self,
        predictors: Sequence[Predictor],
        ranker: Ranker | None = None,
    ) -> None:
        self._predictors = list(predictors)
        self._ranker = ranker or ScoreRanker()

    def suggest(self, text: str) -> list[Suggestion]:
        scored: list[ScoredSuggestion] = []

        for predictor in self._predictors:
            result = predictor.predict(text)
            scored.extend(result.suggestions)

        return self._ranker.rank(scored)
