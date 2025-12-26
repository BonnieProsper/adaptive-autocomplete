from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from aac.ranking.explanation import RankingExplanation


@dataclass(frozen=True)
class CompletionContext:
    text: str
    cursor_pos: int | None = None

    def prefix(self) -> str:
        """
        Returns the stable prefix fragment immediately before the cursor.

        The character directly before the cursor is treated as in-progress
        input and is excluded from the prefix.
        """
        if self.cursor_pos is None:
            return ""

        before = self.text[: self.cursor_pos]
        parts = before.split()

        if not parts:
            return ""

        token = parts[-1]

        # Drop the in-progress character
        return token[:-1] if len(token) > 0 else ""


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
