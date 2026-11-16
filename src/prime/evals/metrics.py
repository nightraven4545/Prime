"""Evaluation metrics and the statistics used to report them."""

from collections.abc import Callable, Sequence

import numpy as np


def recall_at_k(retrieved: Sequence[str], gold: Sequence[str], k: int) -> float:
    """1.0 if any gold passage is in the top k, else 0.0. Averaged over questions this is hit rate@k."""
    return float(bool(set(retrieved[:k]) & set(gold)))


def reciprocal_rank(retrieved: Sequence[str], gold: Sequence[str]) -> float:
    gold_set = set(gold)
    return next((1.0 / rank for rank, doc in enumerate(retrieved, start=1) if doc in gold_set), 0.0)


def numeric_match(predicted: float | None, gold: float, rel_tol: float = 0.005) -> bool:
    """Within 0.5% of gold by default; for gold of zero, within rel_tol absolutely."""
    if predicted is None:
        return False
    return abs(predicted - gold) <= rel_tol * (abs(gold) or 1.0)


def bootstrap_ci(
    values: Sequence[float], n_resamples: int = 2000, level: float = 0.95, seed: int = 0
) -> tuple[float, float, float]:
    """Mean with a percentile bootstrap interval: (mean, low, high)."""
    x = np.asarray(values, dtype=float)
    if x.size == 0:
        raise ValueError("no values")
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, x.size, size=(n_resamples, x.size))].mean(axis=1)
    low, high = np.quantile(means, [(1 - level) / 2, (1 + level) / 2])
    return float(x.mean()), float(low), float(high)


def paired_bootstrap(
    a: Sequence[float], b: Sequence[float], n_resamples: int = 2000, level: float = 0.95, seed: int = 0
) -> tuple[float, float, float]:
    """Mean difference a - b on the same questions, with an interval. Excluding zero means a real gap."""
    if len(a) != len(b):
        raise ValueError("a and b must score the same questions")
    return bootstrap_ci(np.asarray(a, dtype=float) - np.asarray(b, dtype=float), n_resamples, level, seed)


def cohen_kappa(a: Sequence[bool], b: Sequence[bool]) -> float:
    """Agreement between two binary raters beyond chance. 1.0 when both raters are constant and agree."""
    if len(a) != len(b) or not a:
        raise ValueError("raters must label the same non-empty set")
    x, y = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
    observed = float((x == y).mean())
    expected = float(x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean()))
    return 1.0 if expected == 1.0 else (observed - expected) / (1 - expected)


def risk_coverage(confidence: Sequence[float], correct: Sequence[bool]) -> list[tuple[float, float]]:
    """(coverage, error rate) as the abstention threshold falls: answer the most confident first."""
    if len(confidence) != len(correct) or not confidence:
        raise ValueError("need one confidence per answer")
    order = np.argsort(-np.asarray(confidence, dtype=float), kind="stable")
    wrong = np.cumsum(~np.asarray(correct, dtype=bool)[order])
    n = len(order)
    return [((i + 1) / n, float(wrong[i] / (i + 1))) for i in range(n)]


Metric = Callable[[Sequence[str], Sequence[str]], float]
