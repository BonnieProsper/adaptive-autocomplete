from __future__ import annotations

from aac.presets import get_preset
from aac.domain.history import History


def test_history_learning_boosts_selected_value() -> None:
    history = History()
    engine = get_preset("default").build(history)

    before = engine.suggest("he")
    before_values = [s.value for s in before]

    # Simulate user selection via history
    history.record(
        prefix="he",
        value="hero",
    )

    after = engine.suggest("he")
    after_values = [s.value for s in after]

    assert "hero" in after_values

    # Ranking should improve or stay the same
    assert after_values.index("hero") <= before_values.index("hero")
