from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class RankingExplanation:
    """
    Explains how a final ranking score was produced for a suggestion.

    Scoring lifecycle:
    - Predictor produces a base score
    - Learning/ranking layers apply adjustments
    - Final score is derived deterministically

    Invariants:
    - final_score == base_score + history_boost
    - source identifies the originating predictor
    """

    value: str
    base_score: float
    history_boost: float
    final_score: float
    source: str

    def __post_init__(self) -> None:
        """
        Enforce internal consistency.
        """
        expected = self.base_score + self.history_boost
        if abs(self.final_score - expected) > 1e-9:
            raise ValueError(
                "Invalid RankingExplanation: "
                f"final_score ({self.final_score}) "
                f"!= base_score + history_boost ({expected})"
            )

    def to_dict(self) -> dict[str, float | str]:
        """
        Export explanation in a JSON-serializable form.
        """
        return asdict(self)

    def merge(self, other: "RankingExplanation") -> None:
        """
        Safely merge another explanation into this one.
        Only the scores are summed; the source remains unchanged.
        """
        if self.value != other.value:
            raise ValueError("Cannot merge explanations for different values")

        object.__setattr__(self, "base_score", self.base_score + other.base_score)
        object.__setattr__(
            self, "history_boost", self.history_boost + other.history_boost
        )
        object.__setattr__(self, "final_score", self.final_score + other.final_score)

    @staticmethod
    def from_predictor(
        *,
        value: str,
        score: float,
        source: str,
    ) -> RankingExplanation:
        """
        Create an explanation directly from a predictor output.
        """
        return RankingExplanation(
            value=value,
            base_score=score,
            history_boost=0.0,
            final_score=score,
            source=source,
        )

    def apply_history_boost(self, boost: float) -> RankingExplanation:
        """
        Return a new explanation with a learning-based adjustment applied.
        """
        return RankingExplanation(
            value=self.value,
            base_score=self.base_score,
            history_boost=self.history_boost + boost,
            final_score=self.base_score + self.history_boost + boost,
            source=self.source,
        )
