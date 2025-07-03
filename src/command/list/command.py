"""Implementation of the list command for Bagel CLI."""

import pathlib

import rich
import typer

from settings import settings

app = typer.Typer()

MAX_PARTITIONS_DISPLAY: int = 5


@app.command()
def datasets() -> None:
    """List datasets in the Bagel storage directory."""
    dataset_dirs = list(pathlib.Path(settings.DATASET_DIRECTORY).iterdir())
    rich.print(
        f"Found [bold]{len(dataset_dirs)}[/bold] dataset{'s' if len(dataset_dirs) != 1 else ''} in {settings.DATASET_DIRECTORY}"  # noqa: E501
    )
    for dataset_dir in dataset_dirs:
        dataset = dataset_dir.name
        partitions = [partition_dir.name for partition_dir in dataset_dir.iterdir()]
        partitions.sort(key=lambda s: s[-10:])
        n_parts = len(partitions)
        rich.print(f"[bold]{dataset}[/bold]: {n_parts} partition{'s' if n_parts != 1 else ''}")
        lines = partitions
        if n_parts > MAX_PARTITIONS_DISPLAY:
            lines = (
                lines[: (MAX_PARTITIONS_DISPLAY) // 2]
                + ["..."]
                + lines[-(MAX_PARTITIONS_DISPLAY - MAX_PARTITIONS_DISPLAY // 2) :]
            )
        for i, line in enumerate(lines):
            prefix = "├── " if i < len(lines) - 1 else "└── "
            rich.print(f"{prefix}{line}")
