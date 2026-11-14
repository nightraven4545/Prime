import numpy as np
import pandas as pd
import pytest

import prime
from prime import business_case as bc, diagnostic, prioritize
from prime.business_case import Assumptions


# --- finance maths against hand-computed cases ---

def test_npv_by_hand():
    # -100 + 60/1.1 + 60/1.21 = 4.1322...
    assert bc.npv(0.10, [-100, 60, 60]) == pytest.approx(4.1322, abs=1e-4)


def test_npv_zero_rate_is_plain_sum():
    assert bc.npv(0.0, [-100, 30, 30]) == -40


def test_payback_interpolates_within_year():
    # cumulative: -100, -40, 20 -> crosses 40/60 of the way through year 2
    assert bc.payback([-100, 60, 60]) == pytest.approx(1 + 40 / 60)


def test_payback_none_when_never_recovered():
    assert bc.payback([-100, 10, 10]) is None


def test_payback_counts_from_year_zero_for_late_start():
    # nothing happens in year 0; spend in year 1; recovered exactly at end of year 3
    assert bc.payback([0, -50, 25, 25]) == pytest.approx(3.0)


UC = pd.Series({"lever": "cost", "base": "ops", "impact_low": 0.05, "impact_base": 0.10,
                "impact_high": 0.20, "one_time_cr": 20, "run_cr": 5, "ramp_years": 2})


def test_flows_ramp_and_costs():
    a = Assumptions(horizon=3, adoption=1.0)
    # full benefit 100; ramp 50% then 100%; run cost 5 a year after the build year
    np.testing.assert_allclose(bc.flows(UC, {"ops": 1000}, a, start=0), [-20, 45, 95, 95])


def test_flows_delay_shifts_everything():
    a = Assumptions(horizon=3, adoption=1.0, delay=1)
    np.testing.assert_allclose(bc.flows(UC, {"ops": 1000}, a, start=0), [0, -20, 45, 95])


def test_revenue_benefit_is_taken_at_margin():
    uc = UC.copy()
    uc["lever"] = "revenue"
    assert bc.run_rate(uc, {"ops": 1000}, Assumptions(adoption=1.0, revenue_margin=0.4)) == pytest.approx(40)


# --- scoring and prioritization ---

Q = {"dimensions": {"data": {"name": "Data", "questions": {"d1": "", "d2": ""},
                             "enabler": {"name": "Fix data", "one_time_cr": 10, "run_cr": 2}},
                    "technology": {"name": "Tech", "questions": {"k1": "", "k2": ""},
                                   "enabler": {"name": "Fix tech", "one_time_cr": 10, "run_cr": 2}}}}


def test_score_is_mean_and_gate_applies():
    s = diagnostic.score(Q, {"d1": 1, "d2": 2, "k1": 4, "k2": 4})
    assert s.loc["data", "score"] == 1.5 and bool(s.loc["data", "gated"])
    assert s.loc["technology", "score"] == 4 and not s.loc["technology", "gated"]


@pytest.mark.parametrize("answers", [{"d1": 1, "k1": 3, "k2": 3}, {"d1": 6, "d2": 2, "k1": 3, "k2": 3}])
def test_score_rejects_missing_or_out_of_range(answers):
    with pytest.raises(ValueError):
        diagnostic.score(Q, answers)


def test_wave_follows_blockers_and_complexity():
    scores = pd.Series({"data": 1.5, "technology": 4.0})
    ucs = pd.DataFrame({"key_dims": ["technology", "data;technology", "technology"],
                        "complexity": [2, 3, 4]})
    out = prioritize.rank(ucs, scores)
    assert list(out["wave"]) == [1, 2, 2]
    assert list(out["blockers"]) == ["", "data", ""]
    assert out["feasibility"].iloc[0] == pytest.approx(4.25)


def test_unknown_dimension_is_an_error():
    with pytest.raises(ValueError):
        prioritize.rank(pd.DataFrame({"key_dims": ["nope"], "complexity": [3]}), pd.Series({"data": 3.0}))


# --- whole pipeline on the shipped data ---

def test_bank_a_runs_and_adds_up():
    q, bank, ucs = prime.load()
    r = prime.run(q, bank, ucs)
    assert len(r["use_cases"]) == len(ucs)
    assert set(ucs["base"]) <= set(bank["baseline"])
    # total flows = use-case flows minus enabler costs, so the NPVs must reconcile
    a = r["assumptions"]
    enabler_flows = np.r_[-r["enablers"]["one_time_cr"].sum(), [-r["enablers"]["run_cr"].sum()] * a.horizon]
    assert r["npv"] == pytest.approx(r["use_cases"]["npv"].sum() + bc.npv(a.rate, enabler_flows))
    t = r["tornado"]
    assert (t["upside"] >= t["downside"]).all()


# --- memo ---

def test_committed_memo_matches_model_output():
    from pathlib import Path
    from prime import narrative
    q, bank, ucs = prime.load()
    memo = narrative.build_memo(prime.run(q, bank, ucs), bank, q)
    assert memo == (Path(prime.DATA).parent / "docs" / "memo.md").read_text()


def test_number_guard_catches_invented_figures():
    from prime import narrative
    draft = "NPV is ₹626 crore over 5 years."
    assert narrative.numbers("Over 5 years NPV is ₹626 crore.") <= narrative.numbers(draft)
    assert not narrative.numbers("NPV is ₹700 crore over 5 years.") <= narrative.numbers(draft)
