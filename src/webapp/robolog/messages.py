"""Content of the Robolog/messages page."""

import textwrap

import duckdb
from streamlit_ace import st_ace

import streamlit as st

if not st.session_state.get("robolog_path") or not st.session_state.get("topic_reader"):
    st.info("Select a robolog file in the summary page first.")
    st.stop()


with st.container():
    st.write(f"### Robolog ID: {st.session_state.topic_reader.robolog_id}")
    st.caption(st.session_state.robolog_path)
    st.markdown("<br>", unsafe_allow_html=True)


with st.container():
    topic = st.selectbox("Select a topic", st.session_state.topic_reader.topics)
    st.markdown("<br>", unsafe_allow_html=True)


with st.container():
    sql_query = st_ace(
        value=textwrap.dedent(f'''\
        SELECT
        \ttimestamp_seconds,
        \t"{topic}" AS message
        FROM "{topic}" AS topic
        LIMIT 10
        '''),  # noqa: S608
        language="sql",
        theme="clouds",
        height=200,
    )


with st.spinner(f"Retrieving messages from {topic}...", show_time=True):
    dataset = st.session_state.topic_reader.read([topic])
    relation = duckdb.from_arrow(dataset)
    duckdb.register(topic, relation)
    st.markdown("#### Result")
    st.dataframe(duckdb.sql(sql_query).to_df(), hide_index=True)
