from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


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

        # 'cursor_pos' is given as a 1-based index (cursor between characters),
        # so convert to a Python slice index by subtracting 1. Ensure non-negative.
        pos = max(0, self.cursor_pos - 1)
        prefix_part = self.text[:pos]
        parts = prefix_part.split()
        return parts[-1] if parts else ""


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
    explanation: RankingExplanation


@dataclass(frozen=True)
class PredictionResult:
    """
    Output of a single predictor.
    """
    predictor: str
    suggestions: Sequence[ScoredSuggestion]
