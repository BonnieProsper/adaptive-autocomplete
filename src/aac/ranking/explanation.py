from __future__ import annotations

from dataclasses import asdict, dataclass


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
        expected = self.base_score + self.history_boost
        if abs(self.final_score - expected) > 1e-9:
            raise ValueError(
                "Invalid RankingExplanation: "
                f"final_score ({self.final_score}) "
                f"!= base_score + history_boost ({expected})"
            )

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)

    def merge(self, other: RankingExplanation) -> RankingExplanation:
        """
        Return a new explanation representing the merged contribution
        of this explanation and another.

        Only scores are combined; the source remains unchanged.
        """
        if self.value != other.value:
            raise ValueError("Cannot merge explanations for different values")

        return RankingExplanation(
            value=self.value,
            base_score=self.base_score + other.base_score,
            history_boost=self.history_boost + other.history_boost,
            final_score=self.final_score + other.final_score,
            source=self.source,
        )

    @staticmethod
    def from_predictor(
        *,
        value: str,
        score: float,
        source: str,
    ) -> RankingExplanation:
        return RankingExplanation(
            value=value,
            base_score=score,
            history_boost=0.0,
            final_score=score,
            source=source,
        )

    def apply_history_boost(self, boost: float) -> RankingExplanation:
        return RankingExplanation(
            value=self.value,
            base_score=self.base_score,
            history_boost=self.history_boost + boost,
            final_score=self.base_score + self.history_boost + boost,
            source=self.source,
        )
