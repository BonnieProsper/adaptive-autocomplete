from __future__ import annotations

from collections.abc import Iterable, Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import Prediction, Suggestion


class AutocompleteEngine:
    """
    Orchestrates multiple predictors to produce ranked autocomplete suggestions.

    Intentionally dumb for now:
    - no learning
    - no persistence
    - no fusion logic beyond basic aggregation

    Intelligence to be added later.
    """

    def __init__(self, predictors: Sequence[Predictor]) -> None:
        self._predictors = list(predictors)

    def suggest(self, text: str) -> list[Suggestion]:
        predictions: list[Prediction] = []

        for predictor in self._predictors:
            preds = predictor.predict(text)
            predictions.extend(preds)

        # Temporary rule: higher score = better
        predictions.sort(key=lambda p: p.score, reverse=True)

        return [p.suggestion for p in predictions]
