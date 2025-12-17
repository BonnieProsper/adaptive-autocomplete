from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.domain.history import History
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
        aggregated: dict[str, float] = defaultdict(float)

        for predictor in self._predictors:
            for scored in predictor.predict(prefix):
                aggregated[scored.suggestion.value] += scored.score

        # Deterministic baseline order before ranking
        fused = [
            ScoredSuggestion(Suggestion(value), score)
            for value, score in sorted(aggregated.items())
        ]

        return self._ranker.rank(prefix, fused)

    def record_selection(self, prefix: str, value: str) -> None:
        self._history.record(prefix, value)

        for predictor in self._predictors:
            record = getattr(predictor, "record", None)
            if callable(record):
                record(prefix, value)
