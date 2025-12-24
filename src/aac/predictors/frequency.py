from __future__ import annotations

from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion, ensure_context
from aac.ranking.explanation import RankingExplanation


class FrequencyPredictor(Predictor):
    """
    Suggests words based on observed global frequency.
    """
    name = "frequency"

    def __init__(self, frequencies: dict[str, int]) -> None:
        self._freq = dict(frequencies)

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        ctx = ensure_context(ctx)
            
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
                            score=score,
                            source=self.name,
                        ),
                    )
                )

        return results
