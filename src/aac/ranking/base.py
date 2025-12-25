from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion
from aac.ranking.explanation import RankingExplanation


class Ranker(ABC):
    """
    Produces an ordered list of suggestions from scored candidates.
    """

    @abstractmethod
    def rank(
        self,
        text: str,
        scored: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        """
        Rank scored suggestions and return suggestions only.
        """
        raise NotImplementedError

    @abstractmethod
    def explain(
        self,
        text: str,
        scored: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        """
        Produce explanations for ranking decisions.
        """
        raise NotImplementedError
