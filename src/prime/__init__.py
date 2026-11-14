"""Tech & AI Value Diagnostic: maturity -> priorities -> business case -> roadmap."""
from pathlib import Path

import pandas as pd
import yaml

from . import business_case, diagnostic, prioritize, roadmap
from .business_case import Assumptions

DATA = Path(__file__).resolve().parents[2] / "data"


def load(data_dir: Path = DATA):
    """Return (questionnaire, bank, use_cases) from the data folder."""
    questionnaire = yaml.safe_load((data_dir / "questionnaire.yaml").read_text())
    bank = yaml.safe_load((data_dir / "bank_a.yaml").read_text())
    use_cases = pd.read_csv(data_dir / "use_cases.csv")
    return questionnaire, bank, use_cases


def run(questionnaire: dict, bank: dict, use_cases: pd.DataFrame, a: Assumptions = Assumptions()) -> dict:
    """Run all four steps and return every table the app and the memo need."""
    scores = diagnostic.score(questionnaire, bank["responses"])
    ranked = prioritize.rank(use_cases, scores["score"])
    enabler_table = roadmap.enablers(questionnaire, scores["score"])
    table, total = business_case.portfolio(ranked, enabler_table, bank["baseline"], a)
    return {
        "scores": scores,
        "overall": scores["score"].mean(),
        "enablers": enabler_table,
        "use_cases": table,
        "flows": total,
        "npv": business_case.npv(a.rate, total),
        "payback": business_case.payback(total),
        "tornado": business_case.tornado(ranked, enabler_table, bank["baseline"], a),
        "roadmap": roadmap.build(table, enabler_table, questionnaire),
        "assumptions": a,
    }
