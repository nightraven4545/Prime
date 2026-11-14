"""Step 3: cash flows, NPV and payback per use case and for the portfolio (INR crore, pre-tax)."""
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Assumptions:
    scenario: str = "base"         # which impact column to use: low, base or high
    rate: float = 0.12             # discount rate
    horizon: int = 5               # years after year 0
    adoption: float = 0.8          # share of the modelled benefit actually realized
    cost_mult: float = 1.0         # cost overrun multiplier
    delay: int = 0                 # years every start slips by
    revenue_margin: float = 0.5    # share of extra revenue that reaches profit


def npv(rate: float, flows) -> float:
    """Present value of flows, where flows[0] is year 0 and is not discounted."""
    return float(sum(f / (1 + rate) ** t for t, f in enumerate(flows)))


def payback(flows) -> float | None:
    """Years until cumulative cash turns positive (interpolated within the year); None if it never does."""
    cum = np.cumsum(flows)
    negative = np.flatnonzero(cum < 0)
    if negative.size == 0:
        return 0.0
    for t in range(negative[0] + 1, len(cum)):
        if cum[t] >= 0:
            return float(t - 1 + (-cum[t - 1]) / flows[t])
    return None


def run_rate(uc, baseline: dict, a: Assumptions) -> float:
    """Annual profit benefit at full ramp."""
    margin = a.revenue_margin if uc["lever"] == "revenue" else 1.0
    return baseline[uc["base"]] * uc[f"impact_{a.scenario}"] * a.adoption * margin


def flows(uc, baseline: dict, a: Assumptions, start: int) -> np.ndarray:
    """Net cash flow for years 0..horizon: one-time cost in the start year, then a linear ramp."""
    out = np.zeros(a.horizon + 1)
    start += a.delay
    if start > a.horizon:
        return out
    out[start] -= uc["one_time_cr"] * a.cost_mult
    full = run_rate(uc, baseline, a)
    for t in range(start + 1, a.horizon + 1):
        out[t] += full * min(1.0, (t - start) / uc["ramp_years"]) - uc["run_cr"] * a.cost_mult
    return out


def portfolio(ranked: pd.DataFrame, enablers: pd.DataFrame, baseline: dict, a: Assumptions):
    """Return (per-use-case table with npv/payback/run_rate, total net flows including enabler costs)."""
    table = ranked.copy()
    all_flows = [flows(uc, baseline, a, uc["wave"] - 1) for _, uc in table.iterrows()]
    table["run_rate"] = [run_rate(uc, baseline, a) for _, uc in table.iterrows()]
    table["npv"] = [npv(a.rate, f) for f in all_flows]
    table["payback"] = [payback(f) for f in all_flows]
    total = np.sum(all_flows, axis=0) if all_flows else np.zeros(a.horizon + 1)
    # Enablers earn nothing themselves: one-time cost in year 0, run cost every year after.
    total[0] -= enablers["one_time_cr"].sum() * a.cost_mult
    total[1:] -= enablers["run_cr"].sum() * a.cost_mult
    return table, total


def tornado(ranked: pd.DataFrame, enablers: pd.DataFrame, baseline: dict, a: Assumptions) -> pd.DataFrame:
    """Portfolio NPV when one driver at a time moves to its downside and upside value."""
    def value(**change):
        b = replace(a, **change)
        return npv(b.rate, portfolio(ranked, enablers, baseline, b)[1])

    drivers = [
        ("Impact per use case (low / high case)", {"scenario": "low"}, {"scenario": "high"}),
        ("Adoption (60% / 100%)", {"adoption": 0.6}, {"adoption": 1.0}),
        ("Schedule (1-year slip / on time)", {"delay": a.delay + 1}, {}),
        ("Cost (+30% / -10%)", {"cost_mult": 1.3}, {"cost_mult": 0.9}),
        ("Margin on new revenue (40% / 60%)", {"revenue_margin": 0.4}, {"revenue_margin": 0.6}),
        ("Discount rate (14% / 10%)", {"rate": 0.14}, {"rate": 0.10}),
    ]
    rows = [{"driver": d, "downside": value(**lo), "upside": value(**hi)} for d, lo, hi in drivers]
    out = pd.DataFrame(rows)
    out["swing"] = out["upside"] - out["downside"]
    return out.sort_values("swing", ascending=False, ignore_index=True)
