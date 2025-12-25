from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion
from aac.ranking.explanation import RankingExplanation


class Ranker(ABC):
    """
    Base contract for all ranking strategies.

    Rankers operate on scored suggestions and must be:
    - deterministic, stable, non-mutating
    """

    @abstractmethod
    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        """
        Return suggestions ordered by preference.
        """
        raise NotImplementedError

    @abstractmethod
    def explain(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[RankingExplanation]:
        """
        Return ranking explanations aligned with rank().
        """
        raise NotImplementedError
