from __future__ import annotations

from collections.abc import Iterable

from aac.domain.predictor import Predictor
from aac.domain.types import CompletionContext, ScoredSuggestion, Suggestion
from aac.ranking.explanation import RankingExplanation


class PrefixPredictor(Predictor):
    """
    Suggests words that start with the current token.
    """

    def __init__(self, vocabulary: Iterable[str]) -> None:
        # preserve order, remove duplicates
        self._vocabulary = tuple(dict.fromkeys(vocabulary))

    @property
    def name(self) -> str:
        return "prefix"

    def predict(self, ctx: CompletionContext | str) -> list[ScoredSuggestion]:
        if isinstance(ctx, str):
            ctx = CompletionContext(ctx)
        
        text = ctx.text
        token = self._last_token(text)
        if not token:
            return []

        suggestions: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            if word.startswith(token) and word != token:
                score = self._score(token, word)
                suggestions.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(word),
                        score=score,
                        explanation=RankingExplanation.base( 
                            value=word,
                            score=1.0,
                            source=self.name,
                        ),
                    )
                )

        return suggestions

    @staticmethod
    def _last_token(text: str) -> str:
        parts = text.rstrip().split()
        return parts[-1] if parts else ""

    @staticmethod
    def _score(prefix: str, word: str) -> float:
        # shorter completions rank higher
        return 1.0 / (len(word) - len(prefix) + 1)
