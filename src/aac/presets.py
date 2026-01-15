from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aac.domain.history import History
from aac.domain.types import WeightedPredictor
from aac.engine.engine import AutocompleteEngine
from aac.predictors.frequency import FrequencyPredictor
from aac.predictors.history import HistoryPredictor
from aac.predictors.edit_distance import EditDistancePredictor
from aac.ranking.decay import DecayFunction, DecayRanker
from aac.ranking.score import ScoreRanker


# ---------------------------------------------------------------------
# Preset definition
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class EnginePreset:
    """
    Named, validated engine composition.

    A preset represents intent, not configuration detail.
    """
    name: str
    description: str
    build: Callable[[History | None], AutocompleteEngine]


# ---------------------------------------------------------------------
# Preset builders
# ---------------------------------------------------------------------

def _default_engine(history: History | None) -> AutocompleteEngine:
    history = history or History()

    predictors = [
        WeightedPredictor(
            predictor=FrequencyPredictor(
                frequencies={
                    "hello": 100,
                    "help": 80,
                    "helium": 30,
                    "hero": 50,
                }
            ),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=HistoryPredictor(history),
            weight=1.5,
        ),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=[ScoreRanker()],
        history=history,
    )


def _recency_boosted_engine(history: History | None) -> AutocompleteEngine:
    """Engine with explicit recency bias applied at ranking time."""
    history = history or History()

    predictors = [
        WeightedPredictor(
            predictor=FrequencyPredictor(
                frequencies={
                    "hello": 100,
                    "help": 80,
                    "helium": 30,
                    "hero": 50,
                }
            ),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=HistoryPredictor(history),
            weight=1.0,
        ),
    ]

    rankers = [
        ScoreRanker(),  # establish base relevance
        DecayRanker(
            history=history,
            decay=DecayFunction(half_life_seconds=3600),
            weight=2.0,
        ),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=rankers,
        history=history,
    )


def _robust_engine(history: History | None) -> AutocompleteEngine:
    """
    Production-oriented engine:
    - Frequency baseline
    - Learned user behavior
    - Typo tolerance
    - Recency-aware ranking
    """
    history = history or History()

    vocabulary = [
        "hello",
        "help",
        "helium",
        "hero",
        "hex",
        "heap",
    ]

    predictors = [
        WeightedPredictor(
            predictor=FrequencyPredictor(
                frequencies={
                    "hello": 100,
                    "help": 80,
                    "helium": 30,
                    "hero": 50,
                    "hex": 20,
                    "heap": 25,
                }
            ),
            weight=1.0,
        ),
        WeightedPredictor(
            predictor=HistoryPredictor(history),
            weight=1.2,
        ),
        WeightedPredictor(
            predictor=EditDistancePredictor(
                vocabulary=vocabulary,
                max_distance=2,
            ),
            weight=0.4,  # intentionally weak fallback signal
        ),
    ]

    rankers = [
        ScoreRanker(),
        DecayRanker(
            history=history,
            decay=DecayFunction(half_life_seconds=3600),
            weight=1.5,
        ),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=rankers,
        history=history,
    )


def _stateless_engine(_: History | None) -> AutocompleteEngine:
    predictors = [
        WeightedPredictor(
            predictor=FrequencyPredictor(
                frequencies={
                    "hello": 100,
                    "help": 80,
                    "helium": 30,
                    "hero": 50,
                }
            ),
            weight=1.0,
        ),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=ScoreRanker(),
        history=History(),
    )


# ---------------------------------------------------------------------
# Preset registry
# ---------------------------------------------------------------------

PRESETS: dict[str, EnginePreset] = {
    "default": EnginePreset(
        name="default",
        description="Balanced frequency + history-based autocomplete",
        build=_default_engine,
    ),
    "recency": EnginePreset(
        name="recency",
        description="History-aware autocomplete with time decay",
        build=_recency_boosted_engine,
    ),
    "robust": EnginePreset(
        name="robust",
        description="Production-grade autocomplete with typo tolerance and recency learning",
        build=_robust_engine,
    ),
    "stateless": EnginePreset(
        name="stateless",
        description="Pure frequency-based autocomplete (no learning)",
        build=_stateless_engine,
    ),
}


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def available_presets() -> list[str]:
    return sorted(PRESETS.keys())


def get_preset(name: str) -> EnginePreset:
    try:
        return PRESETS[name]
    except KeyError:
        raise ValueError(
            f"Unknown preset '{name}'. "
            f"Available presets: {', '.join(available_presets())}"
        )


def create_engine(preset: str) -> AutocompleteEngine:
    """
    Backwards-compatible factory.
    Prefer build_engine(...) in app layer.
    """
    return get_preset(preset).build(None)


def describe_presets() -> str:
    """
    Human-readable description of all available presets.

    Intended for CLI and documentation output.
    """
    lines: list[str] = []

    for name in available_presets():
        preset = PRESETS[name]
        lines.append(f"{preset.name}")
        lines.append(f"  {preset.description}")

        if name == "default":
            lines.append("  predictors: frequency, history")
            lines.append("  ranking: score-based")
            lines.append("  learning: enabled")
        elif name == "recency":
            lines.append("  predictors: frequency, history")
            lines.append("  ranking: score + recency decay")
            lines.append("  learning: enabled (time-aware)")
        elif name == "robust":
            lines.append("  predictors: frequency, history, edit-distance")
            lines.append("  ranking: score + recency decay")
            lines.append("  learning: enabled (robust)")
        elif name == "stateless":
            lines.append("  predictors: frequency")
            lines.append("  ranking: score-based")
            lines.append("  learning: disabled")

        lines.append("")

    return "\n".join(lines).rstrip()
