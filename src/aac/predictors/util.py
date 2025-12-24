from __future__ import annotations

from typing import Any

from aac.domain.types import ScoredSuggestion, Suggestion


def make_scored(
    value: str,
    score: float,
    explanation: Any | None = None,
) -> ScoredSuggestion:
    """
    Helper for constructing valid ScoredSuggestion objects.

    Enforces predictor invariants:
    - Non-empty suggestion value
    - Float score
    """
    if not value:
        raise ValueError("Suggestion value must be non-empty")

    if not isinstance(score, float):
        raise TypeError("Score must be a float")

    return ScoredSuggestion(
        suggestion=Suggestion(value=value),
        score=score,
        explanation=explanation,
    )
