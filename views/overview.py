import streamlit as st

from prime import narrative, ui
from prime.diagnostic import level

r, q, bank, ucs = ui.result()
f = narrative.facts(r, bank)

st.title("AI value diagnostic")
st.markdown(
    "Where does AI pay off in a bank, what has to be fixed first, and what is it worth? "
    "This tool takes a short maturity assessment and a few financial baselines and turns them into "
    "a ranked set of AI use cases, a business case and a delivery roadmap."
)
ui.sample_note(bank)

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "AI maturity",
    f"{r['overall']:.1f} of 5",
    level(r["overall"], q["scale"]),
    delta_color="off",
    delta_arrow="off",
    help="Average of six dimensions, each scored 1 (ad hoc) to 5 (leading).",
)
c2.metric(
    "Use cases ready now",
    f"{len(f['wave1'])} of {len(r['use_cases'])}",
    help="Use cases that depend on no dimension below the gate and are not highly complex.",
)
c3.metric(
    "Portfolio value (NPV)", narrative.cr(r["npv"]), help="Net present value over the horizon, pre-tax."
)
c4.metric("Payback", narrative.yrs(r["payback"]), help="Time until cumulative cash turns positive.")

st.subheader("What the numbers say")
st.markdown(narrative.recommendation(r, bank, q))

st.subheader("How to use it")
steps = [
    (
        "views/maturity.py",
        "1. Maturity",
        ":material/speed:",
        "Answer 24 questions; see which areas hold AI back.",
    ),
    (
        "views/priorities.py",
        "2. Priorities",
        ":material/scatter_plot:",
        "See which use cases can start now and which must wait.",
    ),
    (
        "views/business_case.py",
        "3. Business case",
        ":material/payments:",
        "Change the assumptions; see value, payback and what moves them.",
    ),
    ("views/roadmap.py", "4. Roadmap", ":material/route:", "Foundations first, then delivery in waves."),
]
cols = st.columns(2)
for i, (page, label, icon, text) in enumerate(steps):
    with cols[i % 2], st.container(border=True):
        st.page_link(page, label=label, icon=icon)
        st.caption(text)

with st.container(border=True):
    st.page_link("views/checks.py", label="Try the AI answer checks", icon=":material/verified:")
    st.caption(
        "Small live demos of how an AI answer about a financial report is checked before it is trusted."
    )

st.download_button(
    "Download the summary (Markdown)",
    narrative.build_memo(r, bank, q),
    file_name="ai-value-diagnostic-summary.md",
    icon=":material/download:",
)
