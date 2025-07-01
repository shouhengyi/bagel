"""An operator that extracts logging messages from a robolog."""

import pathlib
from typing import Any, Final

import duckdb
import pandas as pd
from pydantic import BaseModel

from src.command.extract import validate
from src.reader import factory


class ExtractLogging(BaseModel):
    """An operator that extracts logging messages from a robolog."""

    # Name of the DuckDB view to register
    name: str

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "extract_logging"

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Extracting logging messages into [bold]{self.name}[/bold]"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Extracted logging messages into [bold]{self.name}[/bold]"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractLogging":
        """Return an ExtractLogging instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        return ExtractLogging(name=data["name"])

    def register(
        self,
        robolog_path: str | pathlib.Path,
    ) -> None:
        """Extract logging messages and register the result as a DuckDB view.

        Args:
            robolog_path (str | pathlib.Path): Path to the robolog file or directory.

        """
        reader = factory.make_topic_message_reader(robolog_path)
        relation = duckdb.from_df(
            pd.DataFrame([message.to_dict() for message in reader.logging_messages])
        )
        duckdb.register(self.name, relation)
