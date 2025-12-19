from __future__ import annotations

from collections.abc import Sequence

from aac.domain.history import History
from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.base import Ranker
from aac.ranking.contracts import LearnsFromHistory
from aac.ranking.explanation import RankingExplanation
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

        # SINGLE SOURCE OF TRUTH FOR HISTORY
        if history is not None:
            self._history = history
        elif isinstance(self._ranker, LearnsFromHistory):
            self._history = self._ranker.history
        else:
            self._history = History()

    def score(self, prefix: str) -> list[ScoredSuggestion]:
        """
        Returns ranked suggestions with scores and explanations.
        Deterministic and non-mutating.
        """
        candidates: list[ScoredSuggestion] = []

        for predictor in self._predictors:
            candidates.extend(predictor.predict(prefix))

        return self._ranker.rank(prefix, candidates)

    def suggest(self, prefix: str) -> list[Suggestion]:
        scored = self.score(prefix)
        return [item.suggestion for item in scored]

    def explain(self, prefix: str) -> list[RankingExplanation]:
        scored = self.score(prefix)
        return [item.explanation for item in scored]

    def record_selection(self, prefix: str, value: str) -> None:
        # CENTRAL LEARNING RECORD
        self._history.record(prefix, value)

        # Optional predictor learning
        for predictor in self._predictors:
            record = getattr(predictor, "record", None)
            if callable(record):
                record(prefix, value)
