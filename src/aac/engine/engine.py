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

    def suggest(self, prefix: str) -> list[Suggestion]:
        suggestions = self._predict(prefix)

        scored = [
            ScoredSuggestion(suggestion=s, score=0.0)
            for s in suggestions
        ]

        ranked = self._ranker.rank(prefix, scored)
        return ranked


    def record_selection(self, prefix: str, value: str) -> None:
        """
        Record a user-selected suggestion so future results can adapt.
        """
        self._history.record(prefix, value)
