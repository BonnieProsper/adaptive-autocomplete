from __future__ import annotations

from aac.engine.engine import AutocompleteEngine


def run(
    *,
    engine: AutocompleteEngine,
    text: str,
    limit: int,
) -> None:
    explanations = engine.explain(text)[:limit]

    if not explanations:
        print("(no explanations available(no predictors produced results).)")
        return

    for exp in explanations:
        history = exp.history_boost
        sign = "+" if history > 0 else ""

        print(
            f"{exp.value:12} "
            f"base={exp.base_score:6.2f} "
            f"history={sign}{history:6.2f} "
            f"= {exp.final_score:6.2f} "
            f"[source={exp.source}]"
        )
