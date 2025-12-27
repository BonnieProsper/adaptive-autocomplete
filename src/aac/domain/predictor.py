from __future__ import annotations

from typing import Protocol

from aac.domain.types import CompletionContext, ScoredSuggestion


class Predictor(Protocol):
    """
    Structural contract for autocomplete predictors.

    Predictors:
    - expose a stable, human-readable name
    - accept a CompletionContext (or raw string)
    - return scored suggestions
    """

    name: str  #  DATA ATTRIBUTE, not @property

    def predict(
        self,
        ctx: CompletionContext | str,
    ) -> list[ScoredSuggestion]:
        ...


@dataclass(frozen=True)
class PredictorExplanation:
    """
    Explanation produced by a single predictor.

    This represents a raw signal before any ranking,
    normalization, or aggregation occurs.
    """
    value: str
    score: float
    source: str
