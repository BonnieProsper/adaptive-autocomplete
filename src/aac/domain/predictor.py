from __future__ import annotations

from typing import Protocol

from aac.domain.types import CompletionContext, ScoredSuggestion


class Predictor(Protocol):
    """Protocol for predictor implementations used by the engine.

    Implementations should return a list of 'ScoredSuggestion' for a
    given input text.
    """
    name: str

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ...
