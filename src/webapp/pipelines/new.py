import streamlit as st
from streamlit_ace import st_ace

from src.webapp.pipelines.pipeline import Pipeline, exists

if "pipelines/new/pipeline" not in st.session_state:
    pipeline_name_container = st.empty()

    with pipeline_name_container.container():
        match st.text_input(
            label="Enter pipeline name",
            placeholder="Use snake_case only (e.g., diagnostic_errors)",
        ):
            case "":
                st.stop()
            case name if exists(name):
                st.warning(f"Pipeline '{name}' already exists. Please choose a different name.")
                st.stop()
            case name:
                st.session_state["pipelines/new/pipeline"] = Pipeline(name=name)
                pipeline_name_container.empty()


pipeline = st.session_state["pipelines/new/pipeline"]

st.markdown(f"### Pipeline `{pipeline.name}`")
st.caption(f"{pipeline.file}")

pipeline.content = st_ace(
    value=pipeline.content, placeholder="Enter pipeline definition here...", language="yaml"
)

pipeline.save()

st.write(pipeline.file.read_text(encoding="utf-8"))
