"""Implementation of the clear command for Bagel CLI."""

import humanize
import rich
import typer
from rich import prompt

from settings import settings
from src.cache import clear_all_cache, clear_all_storage

app = typer.Typer()


@app.command()
def cache() -> None:
    """Clear the bagel cache directory."""
    confirm = prompt.Confirm.ask(
        f":rotating_light: Are you sure about clearing the {settings.CACHE_DIRECTORY} directory?",
        default=False,
    )
    if confirm:
        bytes_cleared = humanize.naturalsize(clear_all_cache())
        rich.print(f":broom: {bytes_cleared} cleared from {settings.CACHE_DIRECTORY} directory")
        return
    else:
        rich.print("Deletion aborted")


@app.command()
def storage() -> None:
    """Clear the bagel storage directory."""
    confirm = prompt.Confirm.ask(
        f":rotating_light: Are you sure about clearing the {settings.STORAGE_DIRECTORY} directory?",
        default=False,
    )

    if not confirm:
        rich.print("Deletion aborted")
        return

    double_confirm = prompt.Confirm.ask(
        ":rotating_light: This will [bold red]IRREVERSIBLY[/bold red] delete all the historic artifacts. Just to confirm again, are you sure?",  # noqa: E501
        default=False,
    )

    if double_confirm:
        bytes_cleared = humanize.naturalsize(clear_all_storage())
        rich.print(f":broom: {bytes_cleared} cleared from {settings.STORAGE_DIRECTORY} directory")
        return

    rich.print("Deletion aborted")
