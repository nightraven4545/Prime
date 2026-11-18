"""Step 2: rate each use case on feasibility and place it in a delivery wave."""

import pandas as pd

from .diagnostic import GATE


def rank(use_cases: pd.DataFrame, scores: pd.Series) -> pd.DataFrame:
    """Add feasibility (1-5), blockers and wave (1-3) to the use-case table.

    Feasibility is the mean maturity of the two dimensions the use case leans on,
    shifted a quarter point per complexity step away from 3.
    Wave is 1 plus the number of those dimensions below the gate; a use case of
    complexity 4+ never goes in wave 1.
    """
    out = use_cases.copy()
    dims = out["key_dims"].str.split(";")
    unknown = {d for ds in dims for d in ds} - set(scores.index)
    if unknown:
        raise ValueError(f"Unknown dimension(s) in key_dims: {sorted(unknown)}")
    out["feasibility"] = [
        min(5.0, max(1.0, scores[ds].mean() - 0.25 * (c - 3)))
        for ds, c in zip(dims, out["complexity"], strict=True)
    ]
    out["blockers"] = [";".join(d for d in ds if scores[d] < GATE) for ds in dims]
    n_blocked = out["blockers"].map(lambda b: len(b.split(";")) if b else 0)
    out["wave"] = (1 + n_blocked).where(out["complexity"] < 4, (1 + n_blocked).clip(lower=2))
    return out
