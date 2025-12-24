from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from aac.ranking.explanation import RankingExplanation


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
        pos = max(0, self.cursor_pos - 1)
        parts = self.text[:pos].split()
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
    explanation: RankingExplanation | None = None

    @property
    def value(self) -> str:
        return self.suggestion.value


@dataclass(frozen=True)
class PredictionResult:
    """
    Output of a single predictor.
    """
    predictor: str
    suggestions: Sequence[ScoredSuggestion]


def ensure_context(ctx: CompletionContext | str) -> CompletionContext:
        if isinstance(ctx, str):
            return CompletionContext(ctx)
        return ctx


class Predictor(Protocol):
    name: str

    def predict(self, context: "CompletionContext") -> list["ScoredCompletion"]:
        ...


@dataclass(frozen=True)
class WeightedPredictor:
    predictor: Predictor
    weight: float = 1.0
