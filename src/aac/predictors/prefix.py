from __future__ import annotations

from collections.abc import Iterable

from aac.domain.predictor import Predictor
from aac.domain.types import (
    CompletionContext,
    PredictorExplanation,
    ScoredSuggestion,
    Suggestion,
    ensure_context,
)


class PrefixPredictor(Predictor):
    """
    Suggests words that start with the current token.

    Predictor contract:
    - Emits deterministic base scores (1.0 per match)
    - Does not apply normalization or weighting
    - Ordering follows vocabulary order
    """

    name: str = "prefix"

    def __init__(self, vocabulary: Iterable[str]) -> None:
        # Preserve order, remove duplicates
        self._vocabulary: tuple[str, ...] = tuple(dict.fromkeys(vocabulary))

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)

        token = self._last_token(ctx.text)
        if not token:
            return []

        results: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            if word.startswith(token) and word != token:
                results.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(value=word),
                        score=1.0,
                        explanation=PredictorExplanation(
                            value=word,
                            score=1.0
                            source=self.name
                        ),
                    )
                )

        return results

    @staticmethod
    def _last_token(text: str) -> str:
        parts = text.rstrip().split()
        return parts[-1] if parts else ""
