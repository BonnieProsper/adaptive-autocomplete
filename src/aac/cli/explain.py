from __future__ import annotations

from aac.engine.engine import AutocompleteEngine


def run(
    *,
    engine: AutocompleteEngine,
    text: str,
    limit: int,
) -> None:
    explanations = engine.explain(text)[:limit]

    for exp in explanations:
        print(
            f"{exp.value:12} "
            f"base={exp.base_score:6.2f} "
            f"+ history={exp.history_boost:6.2f} "
            f"= {exp.final_score:6.2f} "
            f"[source={exp.source}]"
        )
