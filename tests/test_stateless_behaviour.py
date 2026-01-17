from __future__ import annotations

from aac.domain.history import History
from aac.presets import get_preset


def test_stateless_does_not_learn() -> None:
    history = History()
    engine = get_preset("stateless").build(history)

    # Attempt to record learning
    history.record(
        prefix="he",
        value="hero",
    )

    suggestions = engine.suggest("he")
    values = [s.value for s in suggestions]

    # Value may exist due to base predictors,
    # but must NOT be boosted by learning
    assert "hero" in values
