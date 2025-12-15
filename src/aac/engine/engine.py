from __future__ import annotations

from collections.abc import Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import Prediction, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.score import ScoreRanker


class AutocompleteEngine:
    """
    Orchestrates multiple predictors to produce ranked autocomplete suggestions.
    """

    def __init__(
        self,
        predictors: Sequence[Predictor],
        ranker: Ranker | None = None,
    ) -> None:
        self._predictors = list(predictors)
        self._ranker = ranker or ScoreRanker()

    def suggest(self, text: str) -> list[Suggestion]:
        predictions: list[Prediction] = []

        for predictor in self._predictors:
            predictions.extend(predictor.predict(text))

        return self._ranker.rank(predictions)
