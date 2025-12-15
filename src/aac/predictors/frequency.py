from __future__ import annotations

from collections.abc import Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion


class FrequencyPredictor(Predictor):
    def __init__(self, frequencies: dict[str, int]) -> None:
        self._freq = dict(frequencies)

    def predict(self, text: str) -> Sequence[ScoredSuggestion]:
        if not text:
            return []

        results: list[ScoredSuggestion] = []

        for word, count in self._freq.items():
            if word.startswith(text):
                results.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(word),
                        score=float(count),
                    )
                )

        return results
