from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RankingExplanation:
    """
    Explains how a final ranking score was produced for a suggestion.
    Invariants:
    - base_score: score produced by predictor
    - history_boost: adjustment from learned signals
    - final_score: base_score + history_boost (+ ranker effects)
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
    def base(*, value: str, score: float, source: str,) -> RankingExplanation:
        """
        Factory for predictor-originated explanations (no learning applied).
        """
        return RankingExplanation(
            value=value,
            base_score=score,
            history_boost=0.0,
            final_score=score,
            source=source,
        )

