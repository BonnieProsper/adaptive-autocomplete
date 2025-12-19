from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import ScoredSuggestion, Suggestion


class Ranker(ABC):
    @abstractmethod
    def rank(
        self,
        prefix: str,
        suggestions: list[ScoredSuggestion],
    ) -> list[Suggestion]:
        ...
