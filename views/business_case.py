import streamlit as st

from prime import narrative, ui

st.title("3. Business case")
st.markdown("Change any assumption below; every page updates. Figures are pre-tax.")
_, bank, _ = ui.data()
ui.assumptions()  # make sure every assumption has a stored value before the widgets read it
ui.sample_note(bank)

with st.container(border=True):
    st.markdown("**Assumptions**")
    a1, a2, a3 = st.columns(3)
    with a1:
        ui.kept(
            st.select_slider,
            "a_scenario",
            "Impact case",
            options=["low", "base", "high"],
            help="Which of the three impact estimates per use case to use.",
        )
        ui.kept(
            st.slider,
            "a_adoption",
            "Adoption",
            min_value=0.4,
            max_value=1.0,
            step=0.05,
            help="Share of the modelled benefit that is actually realised.",
        )
    with a2:
        ui.kept(st.slider, "a_rate", "Discount rate", min_value=0.08, max_value=0.16, step=0.01)
        ui.kept(st.slider, "a_horizon", "Horizon, years", min_value=3, max_value=7)
    with a3:
        ui.kept(
            st.slider,
            "a_cost_mult",
            "Cost multiplier",
            min_value=0.8,
            max_value=1.5,
            step=0.05,
            help="1.3 means every cost runs 30% over plan.",
        )
        ui.kept(
            st.slider,
            "a_revenue_margin",
            "Margin on new revenue",
            min_value=0.2,
            max_value=0.8,
            step=0.05,
            help="Share of extra revenue that becomes profit.",
        )
    with st.expander(f"Bank baselines, {bank['currency']} a year"):
        cols = st.columns(3)
        for i, key in enumerate(bank["baseline"]):
            with cols[i % 3]:
                ui.kept(st.number_input, f"b_{key}", key.replace("_", " ").capitalize(), min_value=0)

r, q, bank, _ = ui.result()
f = narrative.facts(r, bank)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio value (NPV)", narrative.cr(r["npv"]))
c2.metric("Payback", narrative.yrs(r["payback"]))
c3.metric(
    "Yearly benefit at full ramp",
    narrative.cr(f["run_rate"]),
    f"{f['run_rate_share']:.1%} of operating profit",
    delta_color="off",
    delta_arrow="off",
)
c4.metric("Funding needed before payback", narrative.cr(f["peak_funding"]))

left, right = st.columns(2, gap="large")
with left:
    st.plotly_chart(ui.cashflow_chart(r["flows"], bank["currency"]), width="stretch")
    st.caption("Bars: net cash each year (red when negative). Line: running total.")
with right:
    st.plotly_chart(ui.tornado_chart(r["tornado"], r["npv"], bank["currency"]), width="stretch")
    st.caption("Each bar moves one assumption to a low and a high value while the others stay put.")
with st.expander("Show the numbers"):
    st.dataframe(
        r["tornado"]
        .rename(
            columns={
                "driver": "Assumption",
                "downside": "Low case NPV",
                "upside": "High case NPV",
                "swing": "Swing",
            }
        )
        .round(0),
        hide_index=True,
        width="stretch",
    )
