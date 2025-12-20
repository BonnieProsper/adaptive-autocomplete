from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion


class Ranker(ABC):
    @abstractmethod
    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        """
        Rank scored suggestions.
        Deterministic and non-mutating.
        """
        raise NotImplementedError
