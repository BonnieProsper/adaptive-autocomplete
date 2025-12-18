from typing import Protocol, runtime_checkable

from aac.domain.history import History


@runtime_checkable
class LearnsFromHistory(Protocol):
    """
    Contract for rankers that adapt based on user feedback.

    Any ranker implementing this protocol must expose
    a shared History instance used by the engine.
    """

    history: History
