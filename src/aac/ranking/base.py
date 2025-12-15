from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from aac.domain.types import PredictionResult, Suggestion


class Ranker(ABC):
    """Ranks predictions and returns ordered suggestions."""

    @abstractmethod
    def rank(self, predictions: Sequence[Prediction]) -> list[Suggestion]:
        raise NotImplementedError
