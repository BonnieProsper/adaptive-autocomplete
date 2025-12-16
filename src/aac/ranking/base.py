from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from aac.domain.types import ScoredSuggestion, Suggestion


class Ranker(Protocol):
    def rank(
        self,
        prefix: str,
        suggestions: Sequence[ScoredSuggestion],
    ) -> list[Suggestion]:
        ...
