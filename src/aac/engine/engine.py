from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.score import ScoreRanker


class AutocompleteEngine:
    def __init__(
        self,
        predictors: Sequence[Predictor],
        ranker: Ranker | None = None,
        history: History | None = None,
    ) -> None:
        self._predictors = list(predictors)
        self._ranker = ranker or ScoreRanker()
        self._history = history or History()

    def suggest(self, text: str) -> list[Suggestion]:
        aggregated: dict[str, float] = defaultdict(float)

        for predictor in self._predictors:
            for scored in predictor.predict(text):
                aggregated[scored.suggestion.value] += scored.score

        fused = [
            ScoredSuggestion(Suggestion(value), score)
            for value, score in aggregated.items()
        ]

        return self._ranker.rank(text, fused)

    def record_selection(self, prefix: str, value: str) -> None:
        """
        Record a user-selected suggestion so future results can adapt.
        """
        self._history.record(prefix, value)
