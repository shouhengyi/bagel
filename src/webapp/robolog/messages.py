"""Content of the Robolog/messages page."""

import streamlit as st
from settings import settings

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


with st.spinner(f"Retrieving messages from {topic}...", show_time=True):
    dataset = st.session_state.topic_reader.read([topic], peek=True)
    df = dataset.to_table().to_pandas()
    df.set_index(settings.TIMESTAMP_SECONDS_COLUMN_NAME, inplace=True)
    st.dataframe(df.drop(settings.ROBOLOG_ID_COLUMN_NAME, axis=1), hide_index=False)
    st.markdown(f"At most {settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT} messages are displayed.")
