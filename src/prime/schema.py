"""Typed records shared by ingestion, retrieval, the agent and the eval harness."""

from datetime import date

from pydantic import BaseModel


class Fact(BaseModel):
    """One reported number, normalized. `value` is in base units of `unit` (scale already applied)."""

    id: str
    company: str
    concept: str
    canonical_metric: str | None
    value: float
    unit: str
    period_start: date | None
    period_end: date
    fiscal_year: int
    form: str
    accession: str
    passage_id: str | None = None


class Passage(BaseModel):
    id: str
    company: str
    fiscal_year: int
    form: str
    section_path: list[str]
    text: str
    is_table: bool = False
    fact_ids: list[str] = []


class Citation(BaseModel):
    passage_id: str
    quote: str


class Answer(BaseModel):
    answerable: bool
    text: str
    value: float | None = None
    unit: str | None = None
    period: str | None = None
    citations: list[Citation] = []
    calculation: str | None = None


class EvalRecord(BaseModel):
    question_id: str
    config_id: str
    answer: Answer
    retrieved_ids: list[str]
    gold_passage_ids: list[str]
    gold_value: float | None
    checks: dict[str, bool | float]
    tokens_in: int
    tokens_out: int
    cache_read: int
    cost_usd: float
    latency_s: float
    manifest_hash: str
    prompt_version: str
    model: str
    commit: str
