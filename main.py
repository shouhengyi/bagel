"""Entry point for the Bagel CLI application."""

import typer

from src.command.clear import command as clear_command
from src.command.list import command as list_command
from src.command.run import command as run_command
from src.command.up import command as up_command

app = typer.Typer()

app.add_typer(run_command.app)

app.add_typer(up_command.app, name="up", help="Spin up the Bagel webapp or MCP server.")

app.add_typer(list_command.app, name="list", help="List datasets, pipeline definitions, and more.")

app.add_typer(clear_command.app, name="clear", help="Clear bagel's cache or storage directories.")


if __name__ == "__main__":
    app()
