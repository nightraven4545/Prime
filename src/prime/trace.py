"""Cost accounting and JSONL traces: one line per model or tool call."""

import json
import time
from pathlib import Path
from typing import Any

# USD per million tokens: (input, output, cache read). Cache writes are billed at 125% of input.
# The Haiku cache-read price is assumed at 10% of input; confirm against the pricing page before reporting.
PRICES: dict[str, tuple[float, float, float]] = {
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
}
CACHE_WRITE = 1.25


def cost_usd(model: str, tokens_in: int, tokens_out: int, cache_read: int = 0, cache_write: int = 0) -> float:
    """Cost of one call. `tokens_in` is uncached input only, as the API reports it."""
    if model not in PRICES:
        raise ValueError(f"no price for model {model}")
    price_in, price_out, price_read = PRICES[model]
    dollars = (
        (tokens_in + cache_write * CACHE_WRITE) * price_in + tokens_out * price_out + cache_read * price_read
    )
    return dollars / 1_000_000


class Tracer:
    """Append events for one question to a JSONL file."""

    def __init__(self, path: Path, question_id: str) -> None:
        self.path, self.question_id = path, question_id
        path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, kind: str, **fields: Any) -> None:
        record = {"t": time.time(), "question_id": self.question_id, "kind": kind, **fields}
        with self.path.open("a") as f:
            f.write(json.dumps(record, default=str) + "\n")
