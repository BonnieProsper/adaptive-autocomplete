from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion


class HistoryPredictor(Predictor):
    def __init__(self, history: History, weight: float = 1.0) -> None:
        self._history = history
        self._weight = weight

    def predict(self, text: str) -> Sequence[ScoredSuggestion]:
        if not text:
            return []

        counts = self._history.counts_for_prefix(text)
        if not counts:
            return []

        results: list[ScoredSuggestion] = []

        for value, count in counts.items():
            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value),
                    score=count * self._weight,
                )
            )

        return results

    def record(self, prefix: str, value: str) -> None:
        self._history.record(prefix, value)

