"""Streamlit webapp entry point."""

import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Bagel Session",
    page_icon=":bagel:",
)

page = st.navigation(
    {
        "Robolog": [
            st.Page("src/webapp/robolog/summary.py", title="Summary"),
            st.Page("src/webapp/robolog/messages.py", title="Messages"),
            st.Page("src/webapp/robolog/latency.py", title="Latency"),
            st.Page("src/webapp/robolog/logging.py", title="Logging"),
        ],
    },
    position="sidebar",
)

page.run()
