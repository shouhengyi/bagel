"""Implementation of the up command for Bagel CLI."""

import sys

import typer
from streamlit.web import cli

from settings import settings

app = typer.Typer()


@app.command()
def up() -> None:
    """Run the Bagel webapp."""
    sys.argv = [
        "streamlit",
        "run",
        settings.WEBAPP_PATH,
        f"--server.address={settings.WEBAPP_LOCAL_HOST}",
        f"--server.port={settings.WEBAPP_LOCAL_PORT}",
    ]
    sys.exit(cli.main())
