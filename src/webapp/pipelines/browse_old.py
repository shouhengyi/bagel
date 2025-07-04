import pathlib

import streamlit as st
from pydantic import BaseModel
from streamlit_ace import st_ace

from settings import settings
from src.command.run import command, validate

CREATE_PIPELINE_OPTION_TEXT = "✨ Create a New Pipeline ✨"


class Pipeline(BaseModel):
    name: str
    file: pathlib.Path


def load_file(file: pathlib.Path) -> str:
    try:
        with open(file) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_file(file: pathlib.Path, content: str) -> None:
    with open(file, "w") as f:
        f.write(content)


files = list(pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY).glob("*.yaml"))
pipelines = [Pipeline(name=file.stem, file=file) for file in files]

if not st.session_state.get("/pipelines/browse/name"):
    option_container = st.empty()
    with option_container.container():
        option = st.selectbox(
            "Browse or create a pipeline",
            [CREATE_PIPELINE_OPTION_TEXT] + [pipeline.name for pipeline in pipelines],
            index=None,
        )
        if option:
            option_container.empty()
        else:
            st.stop()

    if option == CREATE_PIPELINE_OPTION_TEXT:
        name_container = st.empty()
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
                    file.parent.mkdir(parents=True, exist_ok=True)
                    if not file.exists():
                        file.touch(exist_ok=True)
                    name_container.empty()
            else:
                st.stop()
    else:
        name = option
        file = pathlib.Path(settings.PIPELINE_DEFINITION_DIRECTORY) / f"{name}.yaml"

    initial_content = load_file(file)

    st.session_state["/pipelines/browse/name"] = name
    st.session_state["/pipelines/browse/file"] = file
    st.session_state["/pipelines/browse/initial_content"] = initial_content

else:
    name = st.session_state["/pipelines/browse/name"]
    file = st.session_state["/pipelines/browse/file"]
    initial_content = st.session_state["/pipelines/browse/initial_content"]


with st.container():
    st.markdown(f"### Pipeline {name}")
    st.caption(file)

    content = st_ace(language="yaml", value=initial_content, auto_update=True)
    save_file(file, content)
    st.write("Content:")
    st.write(content)
    st.write("File")
    st.write(load_file(file))
