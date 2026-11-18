import streamlit as st

from prime import ui

r, q, bank, _ = ui.result()
st.title("4. Roadmap")
st.markdown(
    "Foundations come first because they unblock later waves. Use cases that do not pay back within the "
    "horizon are marked **Hold** and should be re-assessed once the foundations are in place."
)
ui.sample_note(bank)
road = r["roadmap"].copy()
road["wave"] = road["wave"].map(lambda w: "Foundation" if w == 0 else f"Wave {w}")
for wave, group in road.groupby("wave", sort=False):
    st.subheader(wave)
    st.dataframe(
        group[["item", "milestone", "measure"]].rename(
            columns={"item": "Initiative", "milestone": "Milestone", "measure": "Success measure"}
        ),
        hide_index=True,
        width="stretch",
    )
