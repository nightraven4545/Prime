"""AI value diagnostic: entry point. Run with `streamlit run app.py`."""

import streamlit as st

st.set_page_config(page_icon=":material/insights:", layout="wide")

pages = {
    "Diagnostic": [
        st.Page("views/overview.py", title="Overview", icon=":material/home:", default=True),
        st.Page("views/maturity.py", title="1. Maturity", icon=":material/speed:"),
        st.Page("views/priorities.py", title="2. Priorities", icon=":material/scatter_plot:"),
        st.Page("views/business_case.py", title="3. Business case", icon=":material/payments:"),
        st.Page("views/roadmap.py", title="4. Roadmap", icon=":material/route:"),
    ],
    "Trust and method": [
        st.Page("views/checks.py", title="Try the AI answer checks", icon=":material/verified:"),
        st.Page("views/method.py", title="Method and limits", icon=":material/menu_book:"),
    ],
}
page = st.navigation(pages)
name = "AI Value Diagnostic for Banks"
st.set_page_config(page_title=name if page.title == "Overview" else f"{page.title.lstrip('1234. ')} · {name}")
page.run()
