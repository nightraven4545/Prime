"""Streamlit front end: answer the questionnaire, see priorities, business case, roadmap and memo."""
import plotly.graph_objects as go
import streamlit as st

import prime
from prime import narrative
from prime.business_case import Assumptions
from prime.diagnostic import GATE, TARGET, level

st.set_page_config(page_title="Tech & AI Value Diagnostic", layout="wide")
BLUE, GREY, RED = "#1f6fb2", "#9aa5b1", "#c0392b"
WAVE_COLOUR = {1: "#1f6fb2", 2: "#7fb0d8", 3: "#c9d3dc"}

q, bank, use_cases = prime.load()

st.title("Tech & AI Value Diagnostic")
st.caption(f"{bank['name']} is a {bank['description'][0].lower() + bank['description'][1:]}. Every figure is an illustrative assumption "
           f"in {bank['currency']}. Change the answers and assumptions to see the recommendation move.")

with st.sidebar:
    st.header("Assumptions")
    a = Assumptions(
        scenario=st.radio("Impact case", ["low", "base", "high"], index=1, horizontal=True),
        rate=st.slider("Discount rate", 0.08, 0.16, 0.12, 0.01, format="%.2f"),
        horizon=st.slider("Horizon (years)", 3, 7, 5),
        adoption=st.slider("Adoption", 0.4, 1.0, 0.8, 0.05),
        cost_mult=st.slider("Cost multiplier", 0.8, 1.5, 1.0, 0.05),
        revenue_margin=st.slider("Margin on new revenue", 0.2, 0.8, 0.5, 0.05),
    )
    st.header("Baselines")
    with st.expander(f"Annual figures, {bank['currency']}"):
        for key, value in bank["baseline"].items():
            bank["baseline"][key] = st.number_input(key.replace("_", " ").capitalize(), 0, None, value, key=key)

tabs = st.tabs(["1 Maturity", "2 Priorities", "3 Business case", "4 Roadmap", "Memo"])

with tabs[0]:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Questionnaire")
        st.caption("1 = ad hoc, 3 = defined, 5 = leading")
        for dim in q["dimensions"].values():
            with st.expander(dim["name"]):
                for qid, text in dim["questions"].items():
                    bank["responses"][qid] = st.slider(text, 1, 5, bank["responses"][qid], key=qid)

r = prime.run(q, bank, use_cases, a)
s, u = r["scores"], r["use_cases"]

with tabs[0]:
    with right:
        st.subheader(f"Overall {r['overall']:.2f} / 5: {level(r['overall'], q['scale'])}")
        order = s.sort_values("score")
        fig = go.Figure(go.Bar(
            x=order["score"], y=order["name"], orientation="h",
            marker_color=[RED if g else BLUE for g in order["gated"]],
            text=[f"{v:.2f}" for v in order["score"]], textposition="outside"))
        fig.add_vline(x=GATE, line_dash="dot", line_color=RED, annotation_text=f"Gate {GATE:.1f}", annotation_position="bottom right")
        fig.add_vline(x=TARGET, line_dash="dot", line_color=GREY, annotation_text=f"Target {TARGET:.1f}", annotation_position="bottom right")
        fig.update_layout(xaxis_range=[0, 5.3], xaxis_title="Score (1-5)", height=340, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, width="stretch")
        gated = list(s[s["gated"]]["name"])
        st.info(f"Below the gate: {narrative.names(gated)}. Use cases that depend on "
                f"{'these dimensions' if len(gated) > 1 else 'this dimension'} wait for a foundation initiative."
                if gated else "No dimension is below the gate, so no use case is blocked.")

with tabs[1]:
    st.subheader("Value against feasibility")
    fig = go.Figure()
    for wave in sorted(u["wave"].unique()):
        w = u[u["wave"] == wave]
        fig.add_trace(go.Scatter(
            x=w["feasibility"], y=w["npv"], mode="markers+text", name=f"Wave {wave}",
            text=w["id"], textposition="top center", customdata=w[["name", "blockers"]],
            hovertemplate="%{customdata[0]}<br>NPV %{y:,.0f}<br>Feasibility %{x:.1f}"
                          "<br>Blocked by: %{customdata[1]}<extra></extra>",
            marker=dict(size=14, color=WAVE_COLOUR[wave], line=dict(width=1, color="#33414e"))))
    fig.add_hline(y=0, line_color=GREY)
    fig.update_layout(xaxis_title="Feasibility (1-5)", yaxis_title=f"NPV, {bank['currency']}",
                      height=460, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(
        u.sort_values(["wave", "npv"], ascending=[True, False])[
            ["id", "name", "domain", "wave", "feasibility", "blockers", "run_rate", "npv", "payback"]],
        hide_index=True, width="stretch",
        column_config={"feasibility": st.column_config.NumberColumn(format="%.1f"),
                       "run_rate": st.column_config.NumberColumn("Run-rate benefit", format="%.0f"),
                       "npv": st.column_config.NumberColumn("NPV", format="%.0f"),
                       "payback": st.column_config.NumberColumn("Payback (years)", format="%.1f")})

with tabs[2]:
    f = narrative.facts(r, bank)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio NPV", narrative.cr(r["npv"]))
    c2.metric("Payback", narrative.yrs(r["payback"]))
    c3.metric("Run-rate benefit", narrative.cr(f["run_rate"]), f"{f['run_rate_share']:.1%} of operating profit",
              delta_color="off", delta_arrow="off")
    c4.metric("Peak funding", narrative.cr(f["peak_funding"]))
    left, right = st.columns(2)
    with left:
        st.subheader("Cash flow by year")
        years = list(range(a.horizon + 1))
        fig = go.Figure()
        fig.add_bar(x=years, y=r["flows"], name="Net cash flow",
                    marker_color=[RED if v < 0 else BLUE for v in r["flows"]])
        fig.add_scatter(x=years, y=r["flows"].cumsum(), name="Cumulative", line=dict(color="#33414e", width=2))
        fig.update_layout(xaxis_title="Year", yaxis_title=bank["currency"], height=380,
                          margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("What moves NPV")
        t = r["tornado"].iloc[::-1]
        fig = go.Figure()
        fig.add_bar(y=t["driver"], x=t["downside"] - r["npv"], base=r["npv"], orientation="h",
                    marker_color=RED, name="Downside")
        fig.add_bar(y=t["driver"], x=t["upside"] - r["npv"], base=r["npv"], orientation="h",
                    marker_color=BLUE, name="Upside")
        fig.add_vline(x=r["npv"], line_color="#33414e")
        fig.update_layout(barmode="overlay", xaxis_title=f"Portfolio NPV, {bank['currency']}", height=380,
                          margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")

with tabs[3]:
    st.subheader("Foundations first, then three waves")
    road = r["roadmap"].copy()
    road["wave"] = road["wave"].map(lambda w: "Foundation" if w == 0 else f"Wave {w}")
    st.dataframe(road[["wave", "item", "milestone", "measure"]], hide_index=True, width="stretch")

with tabs[4]:
    memo = narrative.build_memo(r, bank, q)
    st.download_button("Download memo (Markdown)", memo, file_name="memo.md")
    st.markdown(memo)
