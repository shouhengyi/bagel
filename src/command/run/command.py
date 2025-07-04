"""Implementation of the run command."""

import functools
import pathlib
from collections.abc import Callable, Iterator
from typing import Annotated, Any

import rich
import typer
import yaml
from rich.emoji import Emoji
from rich.markdown import Markdown

from src.command.run import operator, validate
from src.command.run.operator.base import Operator
from src.command.run.operator.save import FileExtension

SPINNER: str = "dots12"

console = rich.console.Console()

app = typer.Typer()


def make_operators_and_tasks(  # noqa: C901, PLR0912, PLR0913
    pipeline_path: pathlib.Path,
    robolog_path: pathlib.Path,
    start_seconds: float | None = None,
    end_seconds: float | None = None,
    output: FileExtension = FileExtension.PARQUET,
    dry_run: bool = False,
) -> Iterator[Operator, Callable[[], Any]]:
    """Parse the pipeline definition YAML file and return operators and their tasks."""
    if not pipeline_path.exists():
        raise FileNotFoundError(pipeline_path)

    if not robolog_path.exists():
        raise FileNotFoundError(robolog_path)

    main_config = yaml.safe_load(pipeline_path.read_text().encode("utf-8"))

    operators = []
    tasks = []

    for operator_type, configs in main_config.items():
        match operator_type:
            case operator.ExtractTopic.YAML_KEYWORD:
                for op in [operator.ExtractTopic.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractType.YAML_KEYWORD:
                for op in [operator.ExtractType.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractFrequency.YAML_KEYWORD:
                for op in [operator.ExtractFrequency.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractLogging.YAML_KEYWORD:
                for op in [operator.ExtractLogging.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(functools.partial(op.register, robolog_path))

            case operator.ExtractMetadata.YAML_KEYWORD:
                for op in [operator.ExtractMetadata.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(functools.partial(op.register, robolog_path))

            case operator.TransformDataFrame.YAML_KEYWORD:
                for op in [operator.TransformDataFrame.from_dict(params) for params in configs]:
                    operators.append(op)
                    tasks.append(op.register)

            case operator.SaveDataFrame.YAML_KEY:
                for name in configs:
                    op = operator.SaveDataFrame.from_name(name)
                    operators.append(op)
                    tasks.append(
                        functools.partial(
                            op.write, robolog_path, start_seconds, end_seconds, output, dry_run
                        )
                    )

            case _:
                raise ValueError(f"Unknown operator type: {operator_type}")

    validate.validate_unique_dataframe_names(
        [op.name for op in operators if not isinstance(op, operator.SaveDataFrame)]
    )

    yield from zip(operators, tasks, strict=True)


@app.command()
def run(  # noqa: PLR0913
    pipeline_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to the pipeline definition YAML file", show_default=False),
    ],
    robolog_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to the robolog", show_default=False),
    ],
    start_seconds: Annotated[float | None, typer.Option(help="Start time in seconds")] = None,
    end_seconds: Annotated[float | None, typer.Option(help="End time in seconds")] = None,
    output: Annotated[
        FileExtension, typer.Option(help="Output file format for saved DataFrames")
    ] = FileExtension.PARQUET,
    dry_run: Annotated[
        bool, typer.Option(help="If true, execute the pipeline without saving results")
    ] = False,
) -> None:
    """Run data pipeline defined in the YAML file on the provided robolog."""
    for op, task in make_operators_and_tasks(
        pipeline_path, robolog_path, start_seconds, end_seconds, output, dry_run
    ):
        with console.status(Markdown(Emoji.replace(f"{op.running_status}")), spinner=SPINNER):
            task()
        console.print(Markdown(Emoji.replace(f"{op.finished_status}")))


def run_webapp(  # noqa: PLR0913
    pipeline_path: pathlib.Path,
    robolog_path: pathlib.Path,
    start_seconds: float | None = None,
    end_seconds: float | None = None,
    output: FileExtension = FileExtension.PARQUET,
    dry_run: bool = False,
) -> None:
    """Run data pipeline defined in the YAML file on the provided robolog in the Bagel webapp."""
    import streamlit as st

    for op, task in make_operators_and_tasks(
        pipeline_path, robolog_path, start_seconds, end_seconds, output, dry_run
    ):
        task()
        st.success(op.finished_status)
