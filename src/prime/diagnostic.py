"""Step 1: score Tech & AI maturity by dimension from questionnaire answers."""

import pandas as pd

GATE = 2.0  # a dimension below this blocks the use cases that depend on it
TARGET = 4.0  # "scaled": the level the gap is measured against


def score(questionnaire: dict, responses: dict) -> pd.DataFrame:
    """One row per dimension: name, score (mean of its answers, 1-5), gap to target, gated flag."""
    rows = []
    for key, dim in questionnaire["dimensions"].items():
        answers = []
        for qid in dim["questions"]:
            if qid not in responses:
                raise ValueError(f"No answer for question {qid}")
            if not 1 <= responses[qid] <= 5:
                raise ValueError(f"Answer for {qid} must be 1-5, got {responses[qid]}")
            answers.append(responses[qid])
        s = sum(answers) / len(answers)
        rows.append(
            {
                "dimension": key,
                "name": dim["name"],
                "score": s,
                "gap": max(TARGET - s, 0.0),
                "gated": s < GATE,
            }
        )
    return pd.DataFrame(rows).set_index("dimension")


def level(s: float, scale: dict) -> str:
    """Label for a score, e.g. 2.25 -> 'Emerging'."""
    return scale[min(5, max(1, round(s)))]
