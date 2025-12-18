from typing import Protocol
from aac.domain.history import History


class LearnsFromHistory(Protocol):
    """
    Contract for rankers that adapt based on user feedback.

    Any ranker implementing this protocol must expose
    a shared History instance used by the engine.
    """

    history: History
