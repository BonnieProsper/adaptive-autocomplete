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
        Return the current word prefix immediately before the cursor.
        """
        if self.cursor_pos <= 0:
            return ""

        i = self.cursor_pos - 1
        text = self.text

        while i >= 0 and text[i].isalnum():
            i -= 1

        return text[i + 1 : self.cursor_pos]


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


class Predictor(Protocol):
    """
    Contract implemented by all predictors.
    """
    name: str

    def predict(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        ...


@dataclass(frozen=True)
class WeightedPredictor:
    """
    Predictor paired with a weight applied during aggregation.
    """
    predictor: Predictor
    weight: float = 1.0

    @property
    def name(self) -> str:
        return self.predictor.name


@dataclass(frozen=True)
class PredictionResult:
    """
    Output of a single predictor before aggregation.
    """
    predictor: str
    suggestions: Sequence[ScoredSuggestion]


def ensure_context(ctx: CompletionContext | str) -> CompletionContext:
    """
    Normalizes raw text or CompletionContext into CompletionContext.
    """
    if isinstance(ctx, CompletionContext):
        return ctx
    return CompletionContext(text=ctx)
