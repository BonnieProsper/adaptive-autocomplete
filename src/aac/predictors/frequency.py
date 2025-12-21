from __future__ import annotations

from collections.abc import Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion
from aac.ranking.explanation import RankingExplanation


class FrequencyPredictor(Predictor):
    """
    Suggests words based on observed global frequency.
    """

    def __init__(self, frequencies: dict[str, int]) -> None:
        self._freq = dict(frequencies)

    def predict(self, ctx: CompletionContext) -> list[ScoredSuggestion]:
        text = ctx.text
        if not text:
            return []

        results: list[ScoredSuggestion] = []

        for word, count in self._freq.items():
            if word.startswith(text):
                score = float(count)
                results.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(word),
                        score=score,
                        explanation=RankingExplanation.base(
                            value=word,
                            base_score=1.0,
                            history_boost=0.0,
                            final_score=1.0,
                            score=score,
                            source="frequency",
                        ),
                    )
                )

        return results
