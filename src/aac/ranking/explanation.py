from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RankingExplanation:
    """
    Explains how a final ranking score was produced for a suggestion.
    """
    value: str
    base_score: float
    history_boost: float
    final_score: float
