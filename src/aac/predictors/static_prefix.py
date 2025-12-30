from __future__ import annotations

from typing import Iterable, List

from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, Prediction


class StaticPrefixPredictor(Predictor):
    """
    Deterministic prefix-based predictor.

    This predictor performs a simple static prefix match against a fixed
    vocabulary. All matches receive a score of 1.0 by design - ranking
    is handled downstream by rankers, not predictors.
    """

    def __init__(self, vocabulary: Iterable[str]):
        self._vocabulary = list(vocabulary)

    def predict(self, ctx: CompletionContext) -> List[Prediction]:
        prefix = ctx.text

        results: List[Prediction] = []

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
