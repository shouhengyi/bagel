"""Content of the Robolog/logging page."""

import pandas as pd

import streamlit as st
from settings import settings

robolog_path = st.session_state.get("robolog_path", None)
topic_reader = st.session_state.get("topic_reader", None)


if not robolog_path or not topic_reader:
    st.info("Select a robolog file in the summary page first.")
    st.stop()


with st.container():
    st.write(f"### Robolog ID: {topic_reader.robolog_id}")
    st.caption(robolog_path)
    st.markdown("<br>", unsafe_allow_html=True)


with st.spinner("Retrieving logging messages...", show_time=True):
    messages = [message.to_dict() for message in topic_reader.logging_messages]


with st.container():
    if not messages:
        st.warning("No logging messages found in this robolog.")
        st.stop()

    df_logging = pd.DataFrame(messages).drop(settings.ROBOLOG_ID_COLUMN_NAME, axis=1)

    all_log_levels = df_logging["level"].unique().tolist()

    col1, col2 = st.columns(2)
    log_levels = col1.multiselect(
        "Select log levels to display",
        all_log_levels,
        default=all_log_levels,
    )
    min_timestamp_seconds, max_timestamp_seconds = col2.slider(
        "Select time range (seconds)",
        min_value=float(df_logging["timestamp_seconds"].min()),
        max_value=float(df_logging["timestamp_seconds"].max()),
        value=(
            float(df_logging["timestamp_seconds"].min()),
            float(df_logging["timestamp_seconds"].max()),
        ),
        step=1.0,
    )

    df_logging = df_logging[df_logging["level"].isin(log_levels)]
    df_logging = df_logging[
        (df_logging["timestamp_seconds"] >= min_timestamp_seconds)
        & (df_logging["timestamp_seconds"] <= max_timestamp_seconds)
    ]

    st.dataframe(df_logging, hide_index=True, height=800)
