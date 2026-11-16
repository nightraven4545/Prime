"""Reciprocal-rank fusion of ranked result lists."""

from collections import defaultdict
from collections.abc import Sequence


def rrf(rankings: Sequence[Sequence[str]], k: int = 60) -> list[str]:
    """Fuse ranked id lists: score(id) = sum over lists of 1 / (k + rank), rank starting at 1.

    Ties keep the order of first appearance, so the result is deterministic.
    """
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(dict.fromkeys(ranking), start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores, key=lambda d: -scores[d])
