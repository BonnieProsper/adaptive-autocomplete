from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreExplanation:
    value: str
    base_score: float
    history_boost: float
    decay_penalty: float
    final_score: float
