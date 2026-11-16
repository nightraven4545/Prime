"""Deterministic checks on an answer before it is shown as fact."""

import re

from prime.schema import Answer, Passage

_NUMBER = re.compile(r"\d[\d,]*\.?\d*")


def _squash(text: str) -> str:
    return " ".join(text.split())


def quote_check(answer: Answer, passages: dict[str, Passage]) -> bool:
    """True when every cited quote is non-empty and appears verbatim (whitespace aside) in its passage.

    An answerable answer with no citations fails.
    """
    if not answer.citations:
        return not answer.answerable
    return all(
        (p := passages.get(c.passage_id)) is not None
        and _squash(c.quote) != ""
        and _squash(c.quote) in _squash(p.text)
        for c in answer.citations
    )


def numbers_in(text: str) -> set[float]:
    return {float(n.replace(",", "").rstrip(".")) for n in _NUMBER.findall(text)}


def number_check(answer: Answer, calculated: float | None = None, rel_tol: float = 1e-6) -> bool:
    """True when the answer's value appears in a cited quote or equals the recorded calculation's result.

    The quoted figure is compared as displayed (for example 4,512 under an "in millions" caption), so
    `answer.value` must be stated in the same displayed scale as the quote, with scale in `answer.unit`.
    """
    if answer.value is None:
        return True
    candidates = {n for c in answer.citations for n in numbers_in(c.quote)}
    if calculated is not None:
        candidates.add(calculated)
    return any(abs(answer.value - n) <= rel_tol * max(1.0, abs(n)) for n in candidates)
