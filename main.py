"""Entry point for the Bagel CLI application."""

import typer

from src.command.clear import command as clear_command
from src.command.extract import command as extract_command
from src.command.up import command as up_command

app = typer.Typer()

app.add_typer(up_command.app)

app.add_typer(extract_command.app)

app.add_typer(clear_command.app, name="clear", help="Clear bagel's cache or storage directories.")


if __name__ == "__main__":
    app()
