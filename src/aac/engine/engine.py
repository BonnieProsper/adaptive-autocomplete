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

    def suggest(self, prefix: str) -> list[Suggestion]:
        scored = self._predict(prefix)
        return self._ranker.rank(prefix, scored)

    def record_selection(self, prefix: str, value: str) -> None:
        for predictor in self._predictors:
            record = getattr(predictor, "record", None)
            if callable(record):
                record(prefix, value)

    def _predict(self, prefix: str) -> list[ScoredSuggestion]:
        aggregated: dict[str, float] = {}

        for predictor in self._predictors:
            for scored in predictor.predict(prefix):
                aggregated[scored.suggestion.value] = (
                    aggregated.get(scored.suggestion.value, 0.0) + scored.score
                )

        return [
            ScoredSuggestion(Suggestion(value), score)
            for value, score in aggregated.items()
        ]
