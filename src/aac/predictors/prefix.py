from __future__ import annotations

from collections.abc import Iterable, Sequence

from aac.domain.predictor import Predictor
from aac.domain.types import ScoredSuggestion, Suggestion


class PrefixPredictor(Predictor):
    """
    Suggests words that start with the current token.
    """

    def __init__(self, vocabulary: Iterable[str]) -> None:
        self._vocabulary = tuple(dict.fromkeys(vocabulary))

    def predict(self, text: str) -> Sequence[ScoredSuggestion]:
        token = self._last_token(text)
        if not token:
            return []

        suggestions: list[ScoredSuggestion] = []

        for word in self._vocabulary:
            if word.startswith(token) and word != token:
                suggestions.append(
                    ScoredSuggestion(
                        suggestion=Suggestion(word),
                        score=self._score(token, word),
                    )
                )

        return suggestions

    @staticmethod
    def _last_token(text: str) -> str:
        parts = text.rstrip().split()
        return parts[-1] if parts else ""

    @staticmethod
    def _score(prefix: str, word: str) -> float:
        # Simple deterministic heuristic: shorter completions rank higher
        return 1.0 / (len(word) - len(prefix) + 1)
