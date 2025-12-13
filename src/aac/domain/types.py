from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True)
class CompletionContext:
    """
    Represents the current completion request.
    """
    text: str
    cursor_pos: int | None = None

    def prefix(self) -> str:
        """
        Returns the token fragment to be completed.
        """
        if self.cursor_pos is None:
            return self.text.split()[-1] if self.text else ""

        return self.text[: self.cursor_pos].split()[-1]


@dataclass(frozen=True)
class Suggestion:
    """
    A candidate completion.
    """
    value: str


@dataclass(frozen=True)
class ScoredSuggestion:
    """
    A suggestion with an associated score.
    """
    suggestion: Suggestion
    score: float


@dataclass(frozen=True)
class PredictionResult:
    """
    Output of a single predictor.
    """
    predictor: str
    suggestions: Sequence[ScoredSuggestion]

