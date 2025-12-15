from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion


class Ranker(ABC):
    """Ranks scored suggestions and returns ordered suggestions."""

    @abstractmethod
    def rank(
        self, suggestions: Sequence[ScoredSuggestion]
    ) -> list[Suggestion]:
        raise NotImplementedError
