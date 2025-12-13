from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    ACCEPTED = "accepted"
    IGNORED = "ignored"


@dataclass(frozen=True)
class FeedbackSignal:
    """
    Represents user feedback on a suggestion.
    """
    predictor: str
    suggestion: str
    feedback: FeedbackType

