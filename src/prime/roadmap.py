"""Step 4: sequence enablers and use cases into waves with a success measure each."""
import pandas as pd

from .diagnostic import GATE

MILESTONE = {
    1: "Live with the first team by month 6; full rollout by month 12",
    2: "Build starts once the blocking enabler is in place; live by month 24",
    3: "Design in year 2; live in year 3",
}
HOLD = "Hold: negative NPV in this horizon; re-run the case once the foundations are live"


def enablers(questionnaire: dict, scores: pd.Series) -> pd.DataFrame:
    """Foundation work for every dimension below the gate."""
    rows = [{"dimension": d, **questionnaire["dimensions"][d]["enabler"]}
            for d in scores.index if scores[d] < GATE]
    return pd.DataFrame(rows, columns=["dimension", "name", "one_time_cr", "run_cr"])


def build(table: pd.DataFrame, enabler_table: pd.DataFrame, questionnaire: dict) -> pd.DataFrame:
    """Rows of the roadmap: enablers first (wave 0), then use cases by wave and NPV."""
    rows = [{"wave": 0, "item": e["name"], "type": "Enabler", "start_year": 0,
             "milestone": "Funded and staffed in quarter 1; first release by month 9",
             "measure": f"{questionnaire['dimensions'][e['dimension']]['name']} score reaches {GATE + 1:.0f} or higher"}
            for _, e in enabler_table.iterrows()]
    for _, uc in table.sort_values(["wave", "npv"], ascending=[True, False]).iterrows():
        target = f"{uc['impact_base']:.1%} " + {
            "cost": "lower", "risk": "lower", "revenue": "higher"}[uc["lever"]]
        rows.append({"wave": uc["wave"], "item": uc["name"], "type": "Use case",
                     "start_year": uc["wave"] - 1,
                     "milestone": MILESTONE[uc["wave"]] if uc["npv"] > 0 else HOLD,
                     "measure": f"{uc['base'].replace('_', ' ').capitalize().replace('Sme', 'SME')} {target} at full ramp"})
    return pd.DataFrame(rows)
