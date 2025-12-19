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
    """
    Orchestrates prediction, ranking, learning, and explanation.

    Single source of truth:
    - History lives here (or is shared with ranker explicitly)
    """

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
        """
        Public API for consumers who don't care about scores.
        """
        return [s.suggestion for s in self.score(prefix)]

    def explain(self, prefix: str) -> list[RankingExplanation]:
        """
        Public API for explainability.
        """
        return [s.explanation for s in self.score(prefix)]

    def record_selection(self, prefix: str, value: str) -> None:
        """
        Records user feedback and propagates learning.
        """
        self._history.record(prefix, value)

        for predictor in self._predictors:
            record = getattr(predictor, "record", None)
            if callable(record):
                record(prefix, value)
