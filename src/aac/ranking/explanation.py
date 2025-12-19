from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RankingExplanation:
    """
    Explains how a final ranking score was produced for a suggestion.
    """
    value: str
    base_score: float
    history_boost: float
    final_score: float
    source: str

    def to_dict(self) -> dict[str, float | str]:
        """
        Export explanation in a JSON-serializable form.
        """
        return asdict(self)

    @staticmethod
    def base(score: float, source: str) -> "RankingExplanation":
        return RankingExplanation(
            base_score=score,
            history_boost=0.0,
            final_score=score,
            source=source,
        )

