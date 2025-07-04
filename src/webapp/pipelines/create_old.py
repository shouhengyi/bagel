"""Content of the Pipelines/create page."""

import pathlib

import streamlit as st
from streamlit_ace import st_ace

from settings import settings
from src.command.run import command, validate

name_container = st.empty()


if not st.session_state.get("/pipelines/create/name") or not st.session_state.get(
    "/pipelines/create/file"
):
    with name_container.container():
        name = st.text_input(
            "Pipeline name", placeholder="Use snake_case only (e.g., diagnostic_errors)"
        )
        if name:
            try:
                validate.validate_snake_case(name)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            file = pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY) / f"{name}.yaml"
            if file.exists():
                st.warning(f"Pipeline '{name}' already exists. Please choose a different name.")
                st.stop()
            else:
                st.session_state["/pipelines/create/name"] = name
                st.session_state["/pipelines/create/file"] = file
                name_container.empty()
        else:
            st.stop()


with st.container():
    name = st.session_state["/pipelines/create/name"]
    file = st.session_state["/pipelines/create/file"]
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)

    st.markdown(f"### Pipeline `{name}`")
    st.caption(f"Created {file}")

    content = st_ace(language="yaml")

    if content:
        file.write_text(content, encoding="utf-8")
    else:
        st.warning("Please define the pipeline before saving.")


with st.container():
    if not content:
        st.stop()

    robolog_path = st.text_input(
        "Please enter a robolog path to **dry run** the pipeline", value=None
    )
    if not robolog_path:
        st.stop()
    if not pathlib.Path(robolog_path).exists():
        st.error(f"Robolog path '{robolog_path}' does not exist.")
        st.stop()

    with st.status(f"DRY RUN pipeline on {robolog_path}", expanded=True):
        command.run_webapp(file, pathlib.Path(robolog_path), dry_run=True)
