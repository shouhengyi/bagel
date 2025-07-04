"""Content of the Robolog/latency page."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from settings import settings
from src.reader import factory

if not st.session_state.get("robolog_path") or not st.session_state.get("topic_reader"):
    st.info("Select a robolog file in the summary page first.")
    st.page_link("src/webapp/robolog/summary.py", label="Go to Summary", icon="👉")
    st.stop()


with st.container():
    st.write(f"### Robolog ID: {st.session_state.topic_reader.robolog_id}")
    st.caption(st.session_state.robolog_path)
    st.markdown("<br>", unsafe_allow_html=True)


with st.container():
    topic = st.selectbox(
        "Select a topic",
        st.session_state.topic_reader.topics,
    )
    st.markdown("<br>", unsafe_allow_html=True)


if not topic:
    st.warning("No topics found in the robolog.")
    st.stop()


with st.spinner(f"Calculating latency for {topic}...", show_time=True):
    freq_reader = factory.make_topic_frequency_reader(st.session_state.robolog_path)
    df_latency = freq_reader.read([topic]).to_table().to_pandas()


with st.container():
    if len(df_latency) <= 1:
        st.warning("Not enough data to calculate latency.")
        st.stop()

    df_latency = df_latency[[settings.TIMESTAMP_SECONDS_COLUMN_NAME, topic]].rename(
        columns={settings.TIMESTAMP_SECONDS_COLUMN_NAME: "Timestamps", topic: "Latency"}
    )

    df_latency["2 Std Dev"] = df_latency["Latency"].mean() + df_latency["Latency"].std() * 2

    col1, col2 = st.columns(2)
    lower_quantile, upper_quantile = col1.slider(
        "Latency quantiles",
        min_value=0,
        max_value=100,
        value=(95, 5),
        step=1,
        format="%u%%",
    )
    window = col2.slider(
        "Rolling window",
        min_value=1,
        max_value=len(df_latency),
        value=max(int(len(df_latency) * 0.2), 1),
        step=10,
    )

    lower_quantile, upper_quantile = lower_quantile / 100, upper_quantile / 100
    lower_name = f"{int(lower_quantile * 100)}% Quantile"
    upper_name = f"{int(upper_quantile * 100)}% Quantile"

    df_latency["lower"] = (
        df_latency["Latency"].rolling(window, min_periods=1).quantile(lower_quantile)
    )
    df_latency["upper"] = (
        df_latency["Latency"].rolling(window, min_periods=1).quantile(upper_quantile)
    )

    fig = px.line(
        df_latency,
        x="Timestamps",
        y=["Latency", "2 Std Dev"],
        height=800,
    )

    fig.add_traces(
        go.Scatter(
            name=lower_name,
            x=df_latency["Timestamps"],
            y=df_latency["lower"],
            line=dict(color="rgba(0,0,0,0)", shape="spline"),
        ),
    )

    fig.add_traces(
        go.Scatter(
            name=upper_name,
            x=df_latency["Timestamps"],
            y=df_latency["upper"],
            line=dict(color="rgba(0,0,0,0)", shape="spline"),
            fill="tonexty",
            fillcolor="rgba(0,0,0,0.1)",
        )
    )

    fig.update_traces(line=dict(width=2, dash="solid"), selector=dict(name="Latency"))

    fig.update_traces(line=dict(color="red", width=1, dash="dash"), selector=dict(name="2 Std Dev"))

    fig.update_layout(
        xaxis=dict(title=dict(text="Timestamp (Seconds)")),
        yaxis=dict(title=dict(text="Latency (Seconds)")),
    )

    st.plotly_chart(fig, use_container_width=True)
