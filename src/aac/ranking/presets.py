from __future__ import annotations

from aac.domain.history import History
from aac.ranking.learning import LearningRanker


def conservative_learning(history: History) -> LearningRanker:
    """
    Mild learning influence.
    Suitable for autocomplete where base scores should dominate.
    """
    return LearningRanker(
        history=history,
        boost=0.25,
        dominance_ratio=0.5,
    )


def balanced_learning(history: History) -> LearningRanker:
    """
    Balanced learning influence.
    Reasonable default for most applications.
    """
    return LearningRanker(
        history=history,
        boost=0.75,
        dominance_ratio=1.0,
    )


def aggressive_learning(history: History) -> LearningRanker:
    """
    Strong learning influence.
    Prioritizes frequently selected items quickly.
    """
    return LearningRanker(
        history=history,
        boost=1.5,
        dominance_ratio=2.0,
    )
