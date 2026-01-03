# TODO
# In README: State that EngineConfig defines global learning policy
# Explain that current rankers accept config for future extension
# Make it explicit that today, only explicit constructor args are used
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    """
    Configuration for learning and ranking behavior.

    This object is intentionally immutable, to make it
    safe to share, deterministic, suitable for testing and reproducibility.
    """

    # How much historical usage influences ranking
    history_weight: float = 0.25

    # Exponential decay rate applied to historical counts
    # Higher = faster forgetting
    decay_rate: float = 0.01

    # Minimum number of observations before history contributes
    min_samples: int = 3
