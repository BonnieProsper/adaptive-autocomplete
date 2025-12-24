from __future__ import annotations

from typing import Protocol

from aac.domain.types import CompletionContext, ScoredSuggestion


class Predictor(Protocol):
    """
    Structural contract for autocomplete predictors.

    Predictors:
    - expose a stable, human-readable name
    - accept a CompletionContext
    - return scored suggestions
    """

    @property
    def name(self) -> str:
        """
        Name of the predictor (used for explainability and debugging).
        """
        ...

    def predict(
        self,
        ctx: CompletionContext | str,
    ) -> list[ScoredSuggestion]:
        """
        Produce scored suggestions for the given context.
        """
        ...
