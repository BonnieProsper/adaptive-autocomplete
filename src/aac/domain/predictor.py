from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from aac.domain.types import ScoredSuggestion


class Predictor(Protocol):
    """Protocol for predictor implementations used by the engine.

    Implementations should return a sequence of `ScoredSuggestion` for a
    given input text.
    """

    def predict(self, text: str) -> Sequence[ScoredSuggestion]:
        ...
