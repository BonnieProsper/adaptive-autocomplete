from __future__ import annotations

from collections.abc import Iterable

from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, Prediction


class StaticPrefixPredictor(Predictor):
    """
    Deterministic prefix-based predictor.

    Performs a static prefix match against a fixed vocabulary.
    All matches receive a neutral score of 1.0 by design.
    Ranking and weighting are handled downstream.
    """

    name: str = "static_prefix"

    def __init__(self, vocabulary: Iterable[str]) -> None:
        # Preserve order, remove duplicates
        self._vocabulary: tuple[str, ...] = tuple(dict.fromkeys(vocabulary))

    def predict(self, ctx: CompletionContext) -> list[Prediction]:
        prefix = ctx.text

        if not prefix:
            return []

        results: list[Prediction] = []

        for word in self._vocabulary:
            if word.startswith(prefix):
                results.append(
                    Prediction(
                        text=word,
                        score=1.0,
                        source=self.name,
                    )
                )

        return results
