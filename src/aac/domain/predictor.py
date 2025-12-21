from __future__ import annotations

from typing import Protocol

from aac.domain.types import CompletionContext, ScoredSuggestion


class Predictor(Protocol):
    """Protocol for predictor implementations used by the engine.

    Implementations should return a sequence of `ScoredSuggestion` for a
    given input text.
    """

    def predict(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        ...
