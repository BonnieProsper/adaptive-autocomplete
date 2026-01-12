from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aac.domain.history import History
from aac.engine import AutocompleteEngine
from aac.predictors.frequency import FrequencyPredictor
from aac.predictors.history import HistoryPredictor
from aac.ranking.decay import DecayFunction, DecayRanker
from aac.ranking.score import ScoreRanker
from aac.domain.types import WeightedPredictor


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
    build: Callable[[], AutocompleteEngine]


# ---------------------------------------------------------------------
# Preset builders
# ---------------------------------------------------------------------

def _default_engine() -> AutocompleteEngine:
    history = History()

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

    rankers = [
        ScoreRanker(),
    ]

    return AutocompleteEngine(
        predictors=predictors,
        ranker=rankers,
        history=history,
    )


def _recency_boosted_engine() -> AutocompleteEngine:
    history = History()

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
        ScoreRanker(),
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


def _stateless_engine() -> AutocompleteEngine:
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
    )


# ---------------------------------------------------------------------
# Preset registry (change to dict)
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


def create_engine(preset: str) -> AutocompleteEngine:
    try:
        return PRESETS[preset].build()
    except KeyError:
        raise ValueError(
            f"Unknown preset '{preset}'. "
            f"Available presets: {', '.join(available_presets())}"
        )
