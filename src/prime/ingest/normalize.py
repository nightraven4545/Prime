"""Turn the number text found in filings into values in base units.

Scale and sign are the commonest silent errors in financial QA, so each rule here is explicit and tested.
"""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

# Words that set a table's scale, as powers of ten. Lakh and crore appear in Indian filers' reports.
SCALE_WORDS = {"thousand": 3, "lakh": 5, "million": 6, "crore": 7, "billion": 9, "trillion": 12}
_CAPTION = re.compile(
    r"\bin\s+(?:[^\s\d]{0,3}\s*|\w+\s+)?(thousand|lakh|million|crore|billion|trillion)s?\b", re.I
)
_BLANK = {"", "-", "–", "—", "n/a", "na", "nm"}


def parse_number(text: str) -> Decimal | None:
    """Parse displayed number text. Brackets and a leading minus mean negative; dashes mean no value."""
    s = text.strip().replace(" ", " ")
    if s.lower() in _BLANK:
        return None
    negative = s.startswith("(") and s.endswith(")") or s.startswith(("-", "−"))
    digits = re.sub(r"[^\d.]", "", s)
    try:
        value = Decimal(digits)
    except InvalidOperation:
        return None
    return -value if negative else value


def ix_value(text: str, scale: int = 0, sign: str | None = None) -> Decimal | None:
    """Value of an inline XBRL fact: displayed text times 10**scale, negated when sign="-".

    In inline XBRL the sign attribute, not brackets in the text, carries negativity.
    """
    value = parse_number(text)
    if value is None:
        return None
    value = abs(value).scaleb(scale)
    return -value if sign == "-" else value


def caption_scale(caption: str) -> int | None:
    """Power of ten stated in a table caption such as "(in millions)" or "₹ in crore"; None if absent."""
    m = _CAPTION.search(caption)
    return SCALE_WORDS[m.group(1).lower()] if m else None


def fiscal_year(period_end: date, fiscal_year_end_month: int) -> int:
    """Fiscal year label for a period, named by the calendar year in which the fiscal year ends.

    A March year-end filer's year to 31 March 2025 is FY2025; so is a December filer's year to 31 Dec 2025.
    """
    if not 1 <= fiscal_year_end_month <= 12:
        raise ValueError(f"month must be 1-12, got {fiscal_year_end_month}")
    return period_end.year + (1 if period_end.month > fiscal_year_end_month else 0)
