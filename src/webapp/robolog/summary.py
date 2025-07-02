"""The content of the Robolog/summary page."""

import pathlib
from datetime import datetime

import humanize
import pandas as pd
import streamlit as st

from src.reader import factory
from src.webapp.utils import stream

input_container = st.empty()


if not st.session_state.get("robolog_path"):
    with input_container.container():
        robolog_path = st.text_input("Please enter a robolog path", value=None)
        if not robolog_path:
            st.stop()
        if not pathlib.Path(robolog_path).exists():
            st.error(f"Robolog path '{robolog_path}' does not exist.")
            st.stop()
        st.session_state.robolog_path = robolog_path


if not st.session_state.get("topic_reader"):
    with st.spinner("Creating robolog reader...", show_time=True):
        st.session_state.topic_reader = factory.make_topic_message_reader(
            st.session_state.robolog_path
        )
        input_container.empty()


with st.container():
    st.write_stream(stream(f"### Robolog ID: {st.session_state.topic_reader.robolog_id}"))
    st.caption(st.session_state.robolog_path)
    st.markdown("<br>", unsafe_allow_html=True)


with st.container():
    col1, col2 = st.columns(2)
    col1.metric("Messages", humanize.intcomma(st.session_state.topic_reader.total_message_count))
    col2.metric("Size", humanize.naturalsize(st.session_state.topic_reader.size_bytes))
    col1.metric(
        "Start Time",
        datetime.fromtimestamp(st.session_state.topic_reader.start_seconds).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )
    col2.metric("Duration", humanize.naturaldelta(st.session_state.topic_reader.duration_seconds))
    st.markdown("<br>", unsafe_allow_html=True)


with st.container():
    df_topics = pd.DataFrame(
        {
            (
                topic,
                st.session_state.topic_reader.type_names[topic],
                humanize.intcomma(st.session_state.topic_reader.message_counts[topic]),
            )
            for topic in st.session_state.topic_reader.topics
        },
        columns=["Topic Name", "Message Type", "Message Count"],
    )
    st.dataframe(df_topics, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)


with st.expander("View all metadata", expanded=False):
    st.json(st.session_state.topic_reader.metadata)
