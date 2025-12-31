from aac.domain.types import WeightedPredictor
from aac.predictors.static_prefix import StaticPrefixPredictor
from aac.predictors.trie import TriePrefixPredictor


def build_prefix_pipeline(vocabulary: list[str]) -> list[WeightedPredictor]:
    """
    Canonical prefix-based predictor pipeline.

    Combines:
    - Static prefix matching (baseline, deterministic)
    - Trie-based prefix matching (scalable)
    """
    return [
        WeightedPredictor(
            predictor=StaticPrefixPredictor(vocabulary),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=TriePrefixPredictor(vocabulary),
            weight=1.0,
        ),
    ]
