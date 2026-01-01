from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    history_weight: float = 0.25
    decay_rate: float = 0.01
    min_samples: int = 3
