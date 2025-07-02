"""Implementation of the run command."""

import functools
import pathlib
from typing import Annotated

import rich
import typer
import yaml

from src.command.run import operator, validate
from src.command.run.operator.save import FileExtension

SPINNER: str = "dots12"

console = rich.console.Console()

app = typer.Typer()


@app.command()
def run(  # noqa: C901, PLR0912
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
) -> None:
    """Run data pipeline defined in the YAML file on the provided robolog."""
    if not pipeline_path.exists():
        raise FileNotFoundError(pipeline_path)

    if not robolog_path.exists():
        raise FileNotFoundError(robolog_path)

    main_config = yaml.safe_load(pipeline_path.read_text().encode("utf-8"))

    dataframes = []
    operators = []
    tasks = []

    for operator_type, configs in main_config.items():
        match operator_type:
            case operator.ExtractTopic.YAML_KEYWORD:
                for op in [operator.ExtractTopic.from_dict(config) for config in configs]:
                    dataframes.append(op.name)
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractType.YAML_KEYWORD:
                for op in [operator.ExtractType.from_dict(config) for config in configs]:
                    dataframes.append(op.name)
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractFrequency.YAML_KEYWORD:
                for op in [operator.ExtractFrequency.from_dict(config) for config in configs]:
                    dataframes.append(op.name)
                    operators.append(op)
                    tasks.append(
                        functools.partial(op.register, robolog_path, start_seconds, end_seconds)
                    )

            case operator.ExtractLogging.YAML_KEYWORD:
                for op in [operator.ExtractLogging.from_dict(config) for config in configs]:
                    dataframes.append(op.name)
                    operators.append(op)
                    tasks.append(functools.partial(op.register, robolog_path))

            case operator.TransformDataFrame.YAML_KEYWORD:
                for op in [operator.TransformDataFrame.from_dict(config) for config in configs]:
                    dataframes.append(op.name)
                    operators.append(op)
                    tasks.append(op.register)

            case operator.SaveDataFrame.YAML_KEY:
                for name in configs:
                    op = operator.SaveDataFrame.from_dict(name)
                    operators.append(op)
                    tasks.append(
                        functools.partial(
                            op.write, robolog_path, start_seconds, end_seconds, output
                        )
                    )

            case _:
                raise ValueError(f"Unknown operator type: {operator_type}")

    validate.validate_unique_dataframe_names(dataframes)

    if not tasks:
        console.print("No tasks to run. Exiting")
        return

    for op, task in zip(operators, tasks, strict=True):
        with console.status(f"{op.running_status}", spinner=SPINNER):
            task()
        console.print(f"{op.finished_status}")

    console.print(f":tada: Finished {len(tasks)} tasks in total :tada:", style="bold green")
