"""An operator that extracts message frequencies from specified topics in a robolog."""

import pathlib
from typing import Any, Final

import duckdb
from pydantic import BaseModel

from src.command.extract import validate
from src.reader import factory


class ExtractFrequency(BaseModel):
    """An operator that extracts message frequencies from specified topics in a robolog."""

    # Name of the DuckDB view to register
    name: str

    # List of topics to extract message frequencies from
    topics: list[str]

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "extract_frequency"

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Extracting frequencies of {len(self.topics)} topics into [bold]{self.name}[/bold]"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Extracted frequencies of {len(self.topics)} topics into [bold]{self.name}[/bold]"  # noqa: E501

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractFrequency":
        """Return an ExtractFrequency instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        return ExtractFrequency(
            name=data["name"],
            topics=data["topics"],
        )

    def register(
        self,
        robolog_path: str | pathlib.Path,
        start_seconds: float | None,
        end_seconds: float | None,
    ) -> None:
        """Extract frequency of messages from topics and register the result as a DuckDB view.

        Args:
            robolog_path (str | pathlib.Path): Path to the robolog file or directory.
            start_seconds (float | None): When to start reading messages.
            end_seconds (float | None): When to stop reading messages.

        """
        reader = factory.make_topic_frequency_reader(robolog_path)
        dataset = reader.read(self.topics, start_seconds, end_seconds)
        relation = duckdb.from_arrow(dataset)
        duckdb.register(self.name, relation)
