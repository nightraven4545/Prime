import streamlit as st

from prime import narrative, ui
from prime.diagnostic import GATE, level

q, bank, _ = ui.data()
st.title("1. AI maturity")
st.markdown(
    f"Six areas decide whether AI reaches production. Each is the average of four questions scored "
    f"1 (ad hoc) to 5 (leading). An area below **{GATE:.0f}** holds back the use cases that depend on it."
)
ui.sample_note(bank)

left, right = st.columns([1, 1], gap="large")
with left:
    st.subheader("Questionnaire")
    for dim in q["dimensions"].values():
        with st.expander(dim["name"]):
            for qid, text in dim["questions"].items():
                ui.kept(
                    st.slider,
                    f"q_{qid}",
                    text,
                    min_value=1,
                    max_value=5,
                    help="1 ad hoc · 2 emerging · 3 defined · 4 scaled · 5 leading",
                )

r, q, bank, _ = ui.result()
s = r["scores"]
with right:
    st.metric(
        "Overall",
        f"{r['overall']:.2f} of 5",
        level(r["overall"], q["scale"]),
        delta_color="off",
        delta_arrow="off",
    )
    st.plotly_chart(ui.maturity_chart(s), width="stretch")
    gated = list(s[s["gated"]]["name"])
    if gated:
        st.warning(
            f"Below the gate: {narrative.names(gated)}. Use cases that depend on "
            f"{'these areas' if len(gated) > 1 else 'this area'} wait for a foundation initiative.",
            icon=":material/block:",
        )
    else:
        st.success("No area is below the gate, so no use case is held back.", icon=":material/check_circle:")
    with st.expander("Show as a table"):
        st.dataframe(
            s[["name", "score", "gap", "gated"]].rename(
                columns={"name": "Area", "score": "Score", "gap": "Gap to target", "gated": "Below gate"}
            ),
            hide_index=True,
            width="stretch",
        )
