from __future__ import annotations

from abc import ABC, abstractmethod


class DecayFunction(ABC):
    """
    Strategy interface for decaying historical learning signals.

    Decay functions are pure and deterministic.
    """

    @abstractmethod
    def apply(self, count: int) -> float:
        """
        Apply decay to a raw selection count.
        """
        raise NotImplementedError


class NoDecay(DecayFunction):
    """
    Identity decay.

    Default behavior: no decay applied.
    """

    def apply(self, count: int) -> float:
        return float(count)


class LinearDecay(DecayFunction):
    """
    Simple linear decay.

    Example:
        count=10, factor=0.5 -> 5.0
    """

    def __init__(self, factor: float) -> None:
        if factor <= 0.0:
            raise ValueError("Decay factor must be positive")
        self._factor = factor

    def apply(self, count: int) -> float:
        return count * self._factor
