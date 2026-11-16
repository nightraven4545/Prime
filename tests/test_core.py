import json
from datetime import date
from decimal import Decimal

import pytest

from prime.agent.calc import calculate
from prime.agent.sqlguard import guard
from prime.agent.verify import number_check, quote_check
from prime.evals import metrics as m
from prime.ingest.normalize import caption_scale, fiscal_year, ix_value, parse_number
from prime.retrieval.fusion import rrf
from prime.schema import Answer, Citation, Passage
from prime.trace import Tracer, cost_usd

# --- normalization ---


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1,234.5", Decimal("1234.5")), ("(1,234)", Decimal("-1234")), ("-12", Decimal("-12")),
     ("$ 4,512", Decimal("4512")), ("—", None), ("", None), ("n/a", None), ("abc", None)],
)  # fmt: skip
def test_parse_number(text, expected):
    assert parse_number(text) == expected


def test_ix_value_applies_scale_and_sign_attribute():
    assert ix_value("4,512", scale=6) == Decimal("4512000000")
    assert ix_value("12.5", scale=-2) == Decimal("0.125")
    # brackets are presentation; the sign attribute decides
    assert ix_value("(300)", scale=3) == Decimal("300000")
    assert ix_value("300", scale=3, sign="-") == Decimal("-300000")


@pytest.mark.parametrize(
    ("caption", "expected"),
    [
        ("(in millions, except per share data)", 6),
        ("₹ in crore", 7),
        ("Rs. in lakhs", 5),
        ("(Dollars in thousands)", 3),
        ("in US$ billions", 9),
        ("Selected data", None),
        ("invested in millionaires", None),
    ],
)
def test_caption_scale(caption, expected):
    assert caption_scale(caption) == expected


def test_fiscal_year_by_year_end_month():
    assert fiscal_year(date(2025, 3, 31), 3) == 2025
    assert fiscal_year(date(2025, 12, 31), 12) == 2025
    assert fiscal_year(date(2024, 6, 30), 3) == 2025  # a quarter inside the March-2025 year
    with pytest.raises(ValueError):
        fiscal_year(date(2025, 3, 31), 13)


# --- fusion ---


def test_rrf_rewards_agreement_and_is_deterministic():
    assert rrf([["a", "b", "c"], ["b", "a", "d"]], k=60)[:2] == ["a", "b"]  # tie -> first seen
    assert rrf([["a", "b"], ["b", "c"], ["b"]])[0] == "b"
    assert rrf([]) == []


# --- calculator ---


def test_calculate():
    assert calculate("(120 - 100) / 100 * 100") == pytest.approx(20)
    assert calculate("-2 ** 2") == -4
    for bad in ["__import__('os').system('ls')", "a + 1", "1 / 0", "2 ** 1000", "1 if 1 else 2", "'a' * 3"]:
        with pytest.raises(ValueError):
            calculate(bad)


# --- SQL guard ---


def test_guard_allows_selects_and_enforces_limit():
    assert guard("select value from facts where company = 'JPM'").upper().endswith("LIMIT 200")
    assert guard("select * from facts limit 5").upper().endswith("LIMIT 5")
    assert guard("select * from facts limit 100000").upper().endswith("LIMIT 200")
    assert "LIMIT" in guard("with t as (select * from facts) select * from t").upper()


@pytest.mark.parametrize(
    "sql",
    [
        "drop table facts",
        "select 1; delete from facts",
        "insert into facts values (1)",
        "select * from secrets",
        "select * from read_csv('/etc/passwd')",
        "select * from main.facts",
        "copy facts to 'x.csv'",
        "attach 'x.db'",
        "not sql at all ((",
        "pragma database_list",
    ],
)
def test_guard_refuses(sql):
    with pytest.raises(ValueError):
        guard(sql)


# --- answer verification ---

P = {"p1": Passage(id="p1", company="X", fiscal_year=2025, form="10-K", section_path=["Item 7"],
                   text="Technology and  communications\nexpense was $4,512 million in 2025.")}  # fmt: skip


def test_quote_check():
    ok = Answer(
        answerable=True, text="t", citations=[Citation(passage_id="p1", quote="expense was $4,512 million")]
    )
    assert quote_check(ok, P)
    assert not quote_check(
        ok.model_copy(update={"citations": [Citation(passage_id="p1", quote="was $9,999")]}), P
    )
    assert not quote_check(
        ok.model_copy(update={"citations": [Citation(passage_id="zz", quote="expense")]}), P
    )
    assert not quote_check(ok.model_copy(update={"citations": [Citation(passage_id="p1", quote="  ")]}), P)
    assert not quote_check(Answer(answerable=True, text="uncited"), P)
    assert quote_check(Answer(answerable=False, text="not disclosed"), P)


def test_number_check():
    cite = [Citation(passage_id="p1", quote="expense was $4,512 million in 2025")]
    assert number_check(Answer(answerable=True, text="t", value=4512, citations=cite))
    assert not number_check(Answer(answerable=True, text="t", value=4521, citations=cite))
    assert number_check(Answer(answerable=True, text="t", value=12.5, citations=cite), calculated=12.5)
    assert number_check(Answer(answerable=True, text="no number", citations=cite))


# --- metrics ---


def test_retrieval_metrics():
    assert m.recall_at_k(["a", "b", "c"], ["c"], 2) == 0.0
    assert m.recall_at_k(["a", "b", "c"], ["c"], 3) == 1.0
    assert m.reciprocal_rank(["a", "b", "c"], ["b", "c"]) == 0.5
    assert m.reciprocal_rank(["a"], ["z"]) == 0.0


def test_numeric_match_tolerance():
    assert m.numeric_match(100.4, 100) and not m.numeric_match(101, 100)
    assert not m.numeric_match(None, 100)
    assert m.numeric_match(0.001, 0) and not m.numeric_match(0.1, 0)


def test_bootstrap_intervals():
    mean, low, high = m.bootstrap_ci([1.0] * 80 + [0.0] * 20)
    assert mean == 0.8 and 0.7 < low < 0.8 < high < 0.9
    assert m.bootstrap_ci([1.0] * 5) == (1.0, 1.0, 1.0)
    diff, low, high = m.paired_bootstrap([1.0] * 60 + [0.0] * 40, [1.0] * 30 + [0.0] * 70)
    assert diff == pytest.approx(0.3) and low > 0  # interval excludes zero
    with pytest.raises(ValueError):
        m.paired_bootstrap([1.0], [1.0, 0.0])


def test_cohen_kappa():
    assert m.cohen_kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert m.cohen_kappa([True, True, False, False], [True, False, True, False]) == 0.0
    # observed 0.75, expected 0.5 -> 0.5
    assert m.cohen_kappa([True, True, False, False], [True, True, True, False]) == pytest.approx(0.5)


def test_risk_coverage_orders_by_confidence():
    curve = m.risk_coverage([0.9, 0.2, 0.8, 0.5], [True, False, True, False])
    assert curve == [(0.25, 0.0), (0.5, 0.0), (0.75, pytest.approx(1 / 3)), (1.0, 0.5)]


# --- cost and tracing ---


def test_cost_usd():
    # 1M uncached in + 1M out on Opus 5.5 = 4 + 20
    assert cost_usd("claude-opus-5-5", 1_000_000, 1_000_000) == pytest.approx(24.0)
    assert cost_usd("claude-opus-5-5", 0, 0, cache_read=1_000_000) == pytest.approx(0.20)
    assert cost_usd("claude-sonnet-5-5", 0, 0, cache_write=1_000_000) == pytest.approx(2.5)
    with pytest.raises(ValueError):
        cost_usd("unknown-model", 1, 1)


def test_tracer_appends_jsonl(tmp_path):
    t = Tracer(tmp_path / "traces" / "q1.jsonl", "q1")
    t.event("tool", name="search_filings", latency_s=0.2)
    t.event("model", tokens_in=10)
    lines = [json.loads(line) for line in (tmp_path / "traces" / "q1.jsonl").read_text().splitlines()]
    assert [e["kind"] for e in lines] == ["tool", "model"] and lines[0]["question_id"] == "q1"
