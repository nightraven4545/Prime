from pathlib import Path

import streamlit as st

st.markdown((Path(__file__).resolve().parents[1] / "docs" / "method.md").read_text())
