"""Shared pieces of the Streamlit app: persistent inputs, the model run, colours and charts."""

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import pipeline
from .business_case import Assumptions
from .diagnostic import GATE, TARGET

# Validated with the dataviz palette checker in light and dark mode (see docs/method.md).
COLOURS = {
    "light": {
        "blue": "#2a78d6",
        "red": "#e34948",
        "critical": "#d03b3b",
        "ink": "#52514e",
        "grid": "#e4e3df",
        "surface": "#ffffff",
        "waves": {1: "#184f95", 2: "#2a78d6", 3: "#86b6ef"},
    },
    "dark": {
        "blue": "#3987e5",
        "red": "#e66767",
        "critical": "#d03b3b",
        "ink": "#c3c2b7",
        "grid": "#383835",
        "surface": "#0e1117",
        "waves": {1: "#86b6ef", 2: "#3987e5", 3: "#184f95"},
    },
}


def colours() -> dict[str, Any]:
    theme = getattr(getattr(st.context, "theme", None), "type", None)
    return COLOURS["dark" if theme == "dark" else "light"]


@st.cache_data
def _data() -> tuple[dict, dict, pd.DataFrame]:
    return pipeline.load()


def data() -> tuple[dict, dict, pd.DataFrame]:
    """Questionnaire, the bank with the visitor's edits applied, and the use-case library."""
    q, bank, ucs = _data()
    bank = {**bank, "responses": dict(bank["responses"]), "baseline": dict(bank["baseline"])}
    for qid in bank["responses"]:
        bank["responses"][qid] = keep(f"q_{qid}", bank["responses"][qid])
    for key in bank["baseline"]:
        bank["baseline"][key] = keep(f"b_{key}", bank["baseline"][key])
    return q, bank, ucs


def keep(key: str, default: Any) -> Any:
    """A value that survives moving between pages (widget state alone is cleared when a page is left)."""
    return st.session_state.setdefault(key, default)


def kept(widget: Any, key: str, label: str, **kwargs: Any) -> Any:
    """Render a widget whose value is stored under `key` and restored on every page."""
    value = widget(label, value=st.session_state[key], key=f"w_{key}", **kwargs)
    st.session_state[key] = value
    return value


ASSUMPTION_DEFAULTS = Assumptions()


def assumptions() -> Assumptions:
    fields = ("scenario", "rate", "horizon", "adoption", "cost_mult", "revenue_margin")
    return Assumptions(**{f: keep(f"a_{f}", getattr(ASSUMPTION_DEFAULTS, f)) for f in fields})


def result() -> tuple[dict, dict, dict, pd.DataFrame]:
    """Run the model on the current inputs. Returns (result, questionnaire, bank, use cases)."""
    q, bank, ucs = data()
    return pipeline.run(q, bank, ucs, assumptions()), q, bank, ucs


def sample_note(bank: dict) -> None:
    st.caption(
        f"{bank['name']} is fictional. Every figure is an illustrative assumption in {bank['currency']}."
    )


def _layout(fig: go.Figure, title: str, height: int, **kwargs: Any) -> go.Figure:
    c = colours()
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16)),
        height=height,
        margin=dict(l=0, r=10, t=56, b=0),
        font=dict(color=c["ink"]),
        hovermode="closest",
        legend=dict(orientation="h", y=-0.18, x=0),
        **kwargs,
    )
    fig.update_xaxes(gridcolor=c["grid"], zerolinecolor=c["grid"])
    fig.update_yaxes(gridcolor=c["grid"], zerolinecolor=c["grid"])
    return fig


def maturity_chart(scores: pd.DataFrame) -> go.Figure:
    c = colours()
    s = scores.sort_values("score")
    names = [f"{n} (below gate)" if g else n for n, g in zip(s["name"], s["gated"], strict=True)]
    fig = go.Figure(
        go.Bar(
            x=s["score"],
            y=names,
            orientation="h",
            text=[f"{v:.2f}" for v in s["score"]],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="#ffffff"),
            marker=dict(color=[c["critical"] if g else c["blue"] for g in s["gated"]], cornerradius=4),
            hovertemplate="%{y}: %{x:.2f} of 5<extra></extra>",
        )
    )
    for x, name in ((GATE, "Gate"), (TARGET, "Target")):
        fig.add_vline(
            x=x,
            line=dict(dash="dot", width=1, color=c["ink"]),
            layer="below",
            annotation=dict(text=f"{name} {x:.0f}", yanchor="bottom", font=dict(size=11)),
        )
    gated = list(s[s["gated"]]["name"])
    best = s.iloc[-1]["name"]
    title = f"{best} is strongest; {len(gated)} below the gate" if gated else f"{best} is strongest"
    return _layout(fig, title, 340, xaxis=dict(range=[0, 5], title="Score, 1 to 5"), showlegend=False)


def priorities_chart(u: pd.DataFrame) -> go.Figure:
    c = colours()
    # Label only the points a reader needs to name (wave 1 and anything that loses money), to the right of
    # the point; points that sit on top of each other share one label.
    labels: dict[str, str] = {}
    spot: dict[tuple[float, int], str] = {}
    for i, f, n, w in u[["id", "feasibility", "npv", "wave"]].itertuples(index=False):
        if w == 1 or n <= 0:
            key = (round(f, 1), round(n / 10))
            if key in spot:
                labels[spot[key]] += f" · {i}"
            else:
                spot[key], labels[i] = i, i
    fig = go.Figure()
    for wave in sorted(u["wave"].unique()):
        w = u[u["wave"] == wave]
        fig.add_trace(
            go.Scatter(
                x=w["feasibility"],
                y=w["npv"],
                mode="markers+text",
                name=f"Wave {wave}",
                text=[labels.get(i, "") for i in w["id"]],
                textposition="middle right",
                cliponaxis=False,
                customdata=w[["id", "name", "blockers"]],
                marker=dict(size=13, color=c["waves"][wave], line=dict(width=2, color=c["surface"])),
                hovertemplate="<b>%{customdata[0]} %{customdata[1]}</b><br>Value (NPV) %{y:,.0f}<br>"
                "Feasibility %{x:.1f} of 5<br>Waiting on: %{customdata[2]}<extra></extra>",
            )
        )
    fig.add_hline(y=0, line=dict(width=1, color=c["ink"]))
    ready = (u["wave"] == 1).sum()
    title = f"{ready} use cases can start now; {(u['npv'] <= 0).sum()} do not pay back"
    pad = (u["feasibility"].min() - 0.1, u["feasibility"].max() + 0.3)
    return _layout(
        fig, title, 440, xaxis=dict(title="Feasibility, 1 to 5", range=pad), yaxis=dict(title="Value (NPV)")
    )


def cashflow_chart(flows: Any, currency: str) -> go.Figure:
    c = colours()
    years = list(range(len(flows)))
    cumulative = pd.Series(flows).cumsum()
    fig = go.Figure()
    fig.add_bar(
        x=years,
        y=flows,
        name="Net cash flow",
        marker=dict(color=[c["red"] if v < 0 else c["blue"] for v in flows], cornerradius=4),
        hovertemplate="Year %{x}: %{y:,.0f}<extra></extra>",
    )
    fig.add_scatter(
        x=years,
        y=cumulative,
        name="Cumulative",
        mode="lines+markers",
        line=dict(color=c["ink"], width=2),
        marker=dict(size=8),
        hovertemplate="Year %{x}, cumulative: %{y:,.0f}<extra></extra>",
    )
    turn = next((y for y, v in zip(years, cumulative, strict=True) if v >= 0 and y > 0), None)
    title = f"Cumulative cash turns positive in year {turn}" if turn else "Cumulative cash stays negative"
    return _layout(fig, title, 380, xaxis=dict(title="Year", dtick=1), yaxis=dict(title=currency))


def tornado_chart(t: pd.DataFrame, npv: float, currency: str) -> go.Figure:
    c = colours()
    t = t.iloc[::-1]
    fig = go.Figure()
    for side, colour, name in (("downside", c["red"], "Downside"), ("upside", c["blue"], "Upside")):
        fig.add_bar(
            y=t["driver"],
            x=t[side] - npv,
            base=npv,
            orientation="h",
            name=name,
            marker=dict(color=colour, cornerradius=4),
            hovertemplate=f"{name}: %{{customdata:,.0f}}<extra>%{{y}}</extra>",
            customdata=t[side],
        )
    fig.add_vline(x=npv, line=dict(width=1, color=c["ink"]))
    title = f"{t.iloc[-1]['driver'].split(' (')[0]} moves the value most"
    return _layout(fig, title, 380, barmode="overlay", xaxis=dict(title=f"Portfolio value (NPV), {currency}"))
