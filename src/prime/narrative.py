"""Write the client memo from model output.

Every figure in the memo is formatted from the model's tables here, in code.
The optional language-model step may only reword the opening paragraph, and its
output is rejected if it contains a number that is not already in the draft.
"""
import re

from . import business_case
from .diagnostic import GATE, TARGET, level

GEN_AI_SOURCE = ("https://www.mckinsey.com/industries/financial-services/our-insights/"
                 "capturing-the-full-value-of-generative-ai-in-banking")


def cr(x: float) -> str:
    return f"₹{x:,.0f} crore"


def yrs(x) -> str:
    return "not within the horizon" if x is None or x != x else f"{x:.1f} years"


def names(items) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def facts(r: dict, bank: dict) -> dict:
    """The numbers the memo quotes, computed once."""
    s, u, a, b = r["scores"], r["use_cases"], r["assumptions"], bank["baseline"]
    impact = r["tornado"].set_index("driver")
    impact_row = impact.loc[[d for d in impact.index if d.startswith("Impact")][0]]
    positive = u[u["npv"] > 0].sort_values("npv", ascending=False)
    op_profit = b["total_income"] - b["operating_expenses"]
    return {
        "overall": r["overall"],
        "best": s["score"].idxmax(),
        "gated": list(s.index[s["gated"]]),
        "wave1": u[u["wave"] == 1].sort_values("npv", ascending=False),
        "hold": u[u["npv"] <= 0].sort_values("npv"),
        "top5_share": positive["npv"].head(5).sum() / positive["npv"].sum(),
        "run_rate": u["run_rate"].sum(),
        "run_rate_share": u["run_rate"].sum() / op_profit,
        "op_profit": op_profit,
        "one_time": (u["one_time_cr"].sum() + r["enablers"]["one_time_cr"].sum()) * a.cost_mult,
        "peak_funding": -min(0.0, r["flows"].cumsum().min()),
        "npv_low": impact_row["downside"],
        "npv_high": impact_row["upside"],
    }


def recommendation(r: dict, bank: dict, q: dict) -> str:
    """The opening paragraph: the answer, stated first."""
    f, a = facts(r, bank), r["assumptions"]
    dim = lambda d: q["dimensions"][d]["name"].lower()
    return (
        f"{bank['name']} should fund {len(f['wave1'])} technology-led AI use cases now, "
        f"spend the first year on {len(f['gated'])} foundations ({'; '.join(dim(d) for d in f['gated'])}), and hold "
        f"{len(f['hold'])} use cases that do not pay back. Even with those included, the programme has a net present value of "
        f"{cr(r['npv'])} over {a.horizon} years at a {a.rate:.0%} discount rate, pays back in "
        f"{yrs(r['payback'])}, and needs {cr(f['peak_funding'])} of funding before it turns cash-positive."
    )


def build_memo(r: dict, bank: dict, q: dict, opening: str | None = None) -> str:
    f, a, s, u = facts(r, bank), r["assumptions"], r["scores"], r["use_cases"]
    name = bank["name"]
    dim = lambda d: q["dimensions"][d]["name"]
    t = r["tornado"]
    score_rows = "\n".join(
        f"| {row['name']} | {row['score']:.2f} | {level(row['score'], q['scale'])} | {row['gap']:.2f} |"
        for _, row in s.iterrows())
    uc_rows = "\n".join(
        f"| {x['wave']} | {x['name']} | {x['feasibility']:.1f} | {x['run_rate']:,.0f} | {x['npv']:,.0f} | "
        f"{yrs(x['payback']) if x['payback'] == x['payback'] else 'none'} |"
        for _, x in u.sort_values(["wave", "npv"], ascending=[True, False]).iterrows())
    tornado_rows = "\n".join(
        f"| {x['driver']} | {x['downside']:,.0f} | {x['upside']:,.0f} |" for _, x in t.iterrows())
    road_rows = "\n".join(
        f"| {x['wave'] or 'Foundation'} | {x['item']} | {x['milestone']} | {x['measure']} |"
        for _, x in r["roadmap"].iterrows())
    flow_rows = " | ".join(f"{v:,.0f}" for v in r["flows"])
    blocked = u[u["blockers"] != ""]

    return f"""# {name}: where AI pays, and what to fix first

*{bank['description']}. All figures are in {bank['currency']} and are illustrative assumptions, not data about a real bank. See `docs/methodology.md`.*

## Recommendation

{opening or recommendation(r, bank, q)}

Three findings support this.

1. **Technology is ahead of the organization around it.** {name} scores {f['overall']:.2f} out of 5 overall. {dim(f['best'])} is the strongest dimension at {s.loc[f['best'], 'score']:.2f}; {names(f"{dim(d)} ({s.loc[d, 'score']:.2f})" for d in f['gated'])} fall below the {GATE:.1f} gate. {len(blocked)} of {len(u)} use cases depend on a gated dimension, so they cannot start until it is fixed.
2. **The value is real, and about half of it sits in five use cases.** At full ramp the portfolio adds {cr(f['run_rate'])} a year to pre-tax profit, {f['run_rate_share']:.1%} of operating profit. The five largest use cases account for {f['top5_share']:.0%} of positive NPV.
3. **Not every use case earns its place.** {names(f['hold']['name'])} {'do' if len(f['hold']) > 1 else 'does'} not recover {'their' if len(f['hold']) > 1 else 'its'} cost within {a.horizon} years because {'they start' if len(f['hold']) > 1 else 'it starts'} late and {'ramp' if len(f['hold']) > 1 else 'ramps'} slowly. Hold {'them' if len(f['hold']) > 1 else 'it'} until the data work is done, then re-run the case; leaving {'them' if len(f['hold']) > 1 else 'it'} out raises NPV by {cr(-f['hold']['npv'].sum())}.

## 1. Maturity: strong platform, weak data and adoption

| Dimension | Score (1-5) | Level | Gap to {TARGET:.0f} |
|---|---|---|---|
{score_rows}

The pattern is common in banks that invested in cloud and platforms before changing how teams work. {name} can deploy a model; it struggles to feed it good data and to get frontline staff to use the result. A dimension below {GATE:.1f} blocks the use cases that depend on it and triggers a foundation initiative:

{chr(10).join(f"- **{dim(e['dimension'])}:** {e['name']} ({cr(e['one_time_cr'])} one-time, {cr(e['run_cr'])} a year)." for _, e in r['enablers'].iterrows())}

## 2. Priorities: start where the bank is already capable

Wave 1 holds the use cases with no blocked dimension and moderate complexity: {names(f['wave1']['name'])}. Together they are worth {cr(f['wave1']['npv'].sum())} in NPV and each pays back within {yrs(f['wave1']['payback'].max())} of the programme start.

| Wave | Use case | Feasibility (1-5) | Run-rate benefit | NPV | Payback |
|---|---|---|---|---|---|
{uc_rows}

Run-rate benefit and NPV are in {bank['currency']}. Payback is measured from the start of the programme, so a wave 2 use case carries its one-year wait.

## 3. Business case: {cr(r['npv'])} NPV, payback in {yrs(r['payback'])}

| Year | {" | ".join(str(i) for i in range(a.horizon + 1))} |
|---|{"---|" * (a.horizon + 1)}
| Net cash flow | {flow_rows} |

One-time investment across use cases and foundations is {cr(f['one_time'])}. The run-rate benefit of {f['run_rate_share']:.1%} of operating profit sits below the 9 to 15 percent that McKinsey estimates for generative AI in banking ([source]({GEN_AI_SOURCE})). The gap is deliberate: this case assumes {a.adoption:.0%} adoption and counts only {a.revenue_margin:.0%} of new revenue as profit.

**What moves the answer.** Portfolio NPV when one driver changes and the rest stay at base:

| Driver | Downside NPV | Upside NPV |
|---|---|---|
{tornado_rows}

Impact per use case and adoption dominate; cost and discount rate matter far less. In the low-impact case NPV falls to {cr(f['npv_low'])}, close to break-even. Management attention should therefore go to measuring realized benefit and frontline usage, more than to squeezing build cost.

## 4. Roadmap

| Wave | Initiative | Milestone | Success measure |
|---|---|---|---|
{road_rows}

## 5. Risks and next steps

- **Impact estimates are the weakest input.** Run a four-week measured pilot on the two largest wave 1 use cases before committing wave 2 funding.
- **Adoption is the second-largest swing.** Put usage and realized-benefit targets in line managers' scorecards from the first release.
- **The data foundation is on the critical path** for {len(u[u['blockers'].str.contains('data')])} use cases. Give it a named owner and review it monthly.
- **Next step:** confirm the baselines in section 3 with finance, then take wave 1 and the two foundations to the investment committee.
"""


NUMBER = re.compile(r"\d[\d,]*\.?\d*")


def numbers(text: str) -> set[str]:
    return {n.replace(",", "").rstrip(".") for n in NUMBER.findall(text)}


def polish(draft: str, model: str = "claude-opus-5-5") -> str:
    """Ask Claude to tighten the opening paragraph. Falls back to the draft on any failure.

    The reply is accepted only if it introduces no number that is absent from the draft.
    """
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.beta.messages.create(
            model=model,
            max_tokens=2000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low"},
            system=("You edit one paragraph of a consulting memo. Keep every number, name and claim exactly as "
                    "given. Do not add facts or figures. Lead with the recommendation. Plain words, three "
                    "sentences at most. Reply with the paragraph only."),
            messages=[{"role": "user", "content": draft}],
        )
        if response.stop_reason != "end_turn":
            return draft
        text = "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception:  # no SDK, no credentials, network or API error: the offline draft is the product
        return draft
    return text if text and numbers(text) <= numbers(draft) else draft


if __name__ == "__main__":
    import sys

    import prime

    q, bank, ucs = prime.load()
    result = prime.run(q, bank, ucs)
    opening = polish(recommendation(result, bank, q)) if "--llm" in sys.argv else None
    sys.stdout.write(build_memo(result, bank, q, opening))
