import streamlit as st

from prime import ui

r, q, bank, _ = ui.result()
u = r["use_cases"]
st.title("2. Priorities")
st.markdown(
    "Each use case is placed by **value** (net present value) and **feasibility** (how ready the areas it "
    "depends on are). Wave 1 can start now; later waves wait for the foundations they need."
)
ui.sample_note(bank)

st.plotly_chart(ui.priorities_chart(u), width="stretch")
st.caption("Labelled points: wave 1 and every use case that does not pay back. Hover any point for details.")

table = u.sort_values(["wave", "npv"], ascending=[True, False])[
    ["id", "name", "domain", "wave", "feasibility", "blockers", "run_rate", "npv", "payback"]
]
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={
        "id": "ID",
        "name": "Use case",
        "domain": "Area",
        "wave": "Wave",
        "feasibility": st.column_config.NumberColumn("Feasibility", format="%.1f"),
        "blockers": "Waiting on",
        "run_rate": st.column_config.NumberColumn(
            "Yearly benefit", format="%,.0f", help=f"At full ramp, {bank['currency']}"
        ),
        "npv": st.column_config.NumberColumn("Value (NPV)", format="%,.0f"),
        "payback": st.column_config.NumberColumn("Payback, years", format="%.1f"),
    },
)
st.download_button(
    "Download this table (CSV)",
    table.to_csv(index=False),
    file_name="use-cases.csv",
    icon=":material/download:",
)
