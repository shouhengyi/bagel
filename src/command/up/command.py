"""Implementation of the up command for Bagel CLI."""

import typer
from streamlit.web import cli

from settings import settings

app = typer.Typer()


@app.command()
def up() -> None:
    """Run the Bagel webapp."""
    cli.main_run([settings.WEBAPP_PATH])
