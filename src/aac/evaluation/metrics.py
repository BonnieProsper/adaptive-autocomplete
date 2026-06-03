"""
Standard IR metrics: precision, recall, MRR, NDCG, average precision.

All functions take a ranked list, a relevant set, and a cutoff depth k.
Return float in [0.0, 1.0], or 0.0 if relevant is empty.
"""
from __future__ import annotations

import math


def precision_at_k(
    ranked_list: list[str],
    relevant: set[str],
    k: int,
) -> float:
    """P@k = |relevant ∩ top_k| / k."""
    if k <= 0 or not relevant:
        return 0.0
    top_k = ranked_list[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / k


def recall_at_k(
    ranked_list: list[str],
    relevant: set[str],
    k: int,
) -> float:
    """R@k = |relevant ∩ top_k| / |relevant|."""
    if not relevant:
        return 0.0
    top_k = set(ranked_list[:k])
    hits = len(top_k & relevant)
    return hits / len(relevant)


def mrr_at_k(
    ranked_list: list[str],
    relevant: set[str],
    k: int,
) -> float:
    """1/rank_of_first_relevant, or 0 if nothing relevant in top-k."""
    if k <= 0 or not relevant:
        return 0.0
    for rank, item in enumerate(ranked_list[:k], start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    ranked_list: list[str],
    relevant: set[str],
    k: int,
    *,
    grades: dict[str, float] | None = None,
) -> float:
    """NDCG@k = DCG@k / IDCG@k. Supports graded relevance via grades dict."""
    if k <= 0 or not relevant:
        return 0.0

    def _gain(item: str) -> float:
        if item not in relevant:
            return 0.0
        if grades:
            return grades.get(item, 1.0)
        return 1.0

    def _dcg(items: list[str]) -> float:
        return sum(
            _gain(item) / math.log2(rank + 1)
            for rank, item in enumerate(items[:k], start=1)
        )

    dcg = _dcg(ranked_list)

    # Ideal DCG: sort relevant items by grade (or all gain=1 if no grades)
    if grades:
        ideal_items = sorted(relevant, key=lambda x: grades.get(x, 1.0), reverse=True)
    else:
        ideal_items = list(relevant)

    idcg = _dcg(ideal_items)

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def average_precision(
    ranked_list: list[str],
    relevant: set[str],
    k: int,
) -> float:
    """AP@k = (1/|relevant|) * sum of P@i for each relevant item at rank i."""
    if not relevant:
        return 0.0

    hits = 0
    precision_sum = 0.0
    for rank, item in enumerate(ranked_list[:k], start=1):
        if item in relevant:
            hits += 1
            precision_sum += hits / rank

    return precision_sum / len(relevant)
