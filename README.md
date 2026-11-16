# Prime

A filings analyst agent with a measured evaluation harness. It is being built to answer questions about banks' technology and AI spending from their SEC filings, cite the exact passages and reported figures it used, decline when the filings do not say, and report how often it is right, what it costs and where it fails.

## Status

**In progress. There are no results yet.**

| Part | State |
|---|---|
| Scaffold: `uv`, `ruff`, strict `mypy`, `pytest`, CI workflow | Done |
| Core logic with tests (below) | Done, 39 tests |
| Ingestion from SEC EDGAR, parsing, inline-XBRL fact extraction | Not started: needs network access to `sec.gov` |
| Embedding and hybrid index | Not started: needs the corpus and a model download |
| Agent loop, tools, structured answers | Not started |
| Evaluation runs, ablations, failure analysis | Not started: needs the above and an API key |
| API, UI, Docker | Not started |

## What exists

| Module | What it does |
|---|---|
| `prime/schema.py` | Typed records: `Fact`, `Passage`, `Citation`, `Answer`, `EvalRecord` |
| `prime/ingest/normalize.py` | Number parsing, inline-XBRL scale and sign, table-caption scale (thousand, lakh, million, crore, billion), fiscal-year labelling for March and December year-ends |
| `prime/retrieval/fusion.py` | Reciprocal-rank fusion |
| `prime/agent/calc.py` | Arithmetic for the agent, parsed with `ast`, no `eval` |
| `prime/agent/sqlguard.py` | Lets the agent run one read-only `SELECT` on whitelisted tables with an enforced row limit; refuses everything else, including table functions that read files |
| `prime/agent/verify.py` | Checks that every cited quote appears verbatim in its passage and that the answer's figure appears in a quote or matches the recorded calculation |
| `prime/evals/metrics.py` | Recall@k, reciprocal rank, numeric match, bootstrap and paired-bootstrap intervals, Cohen's kappa, risk-coverage curve |
| `prime/trace.py` | Cost per call from token counts, JSONL traces |

## Run

```bash
uv sync
make check     # ruff, mypy --strict, pytest
```

## Design

The evaluation is the point of the project. Three ideas carry it:

1. **Exact labels from inline XBRL.** Filings tag each reported number in the HTML, so the passage containing every fact is known. That gives retrieval ground truth without hand labelling.
2. **Reading versus remembering.** A closed-book baseline measures what the model already knows, and a copy of the corpus with altered numbers measures how often the agent follows the document.
3. **Risk and coverage, not one accuracy number.** Deterministic quote and number checks plus a support score decide when to abstain; the trade-off is reported as a curve.
