from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.explanation import RankingExplanation


class HistoryPredictor(Predictor):
    """
    Suggests completions based on exact historical prefix matches.
    """

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
            score = count * self._weight
            results.append(
                ScoredSuggestion(
                    suggestion=Suggestion(value),
                    score=score,
                    explanation=RankingExplanation.base(
                        score=score,
                        source="history_predictor",
                    ),
                )
            )

        return results

    def record(self, prefix: str, value: str) -> None:
        self._history.record(prefix, value)
