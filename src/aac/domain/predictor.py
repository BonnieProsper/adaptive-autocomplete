from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from aac.domain.types import CompletionContext, ScoredSuggestion


class Predictor(Protocol):
    """Protocol for predictor implementations used by the engine.

    Implementations should return a list of 'ScoredSuggestion' for a
    given input text.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the predictor.
        """
        raise NotImplementedError

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ...
