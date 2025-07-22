"""Implementation of the up command for Bagel CLI."""

import subprocess

import typer

from settings import settings

app = typer.Typer()


@app.command()
def webapp() -> None:
    """Run the Bagel webapp."""
    command = [
        "uv",
        "run",
        "streamlit",
        "run",
        settings.WEBAPP_PATH,
        f"--server.address={settings.LOCAL_HOST}",
        f"--server.port={settings.WEBAPP_LOCAL_PORT}",
    ]
    subprocess.run(command, capture_output=False, text=True, check=True)  # noqa: S603


@app.command()
def mcp() -> None:
    """Run the Bagel MCP server."""
    command = [
        "uv",
        "run",
        settings.MCP_PATH,
        "--transpose",
        "sse",
    ]
    subprocess.run(command, capture_output=False, text=True, check=True)  # noqa: S603
