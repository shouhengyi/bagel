"""An operator that extracts messages from specified topics in a robolog."""

import pathlib
from typing import Any, Final

import duckdb
from pydantic import BaseModel

from src.command.extract import validate
from src.reader import factory


class ExtractTopic(BaseModel):
    """An operator that extracts messages from specified topics in a robolog."""

    # Name of the DuckDB view to register
    name: str

    # List of topics to extract messages from
    topics: list[str]

    # Whether to perform a forward fill on the topics
    ffill: bool

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "extract_topic"

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Extracting messages from {len(self.topics)} topics into [bold]{self.name}[/bold]"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Extracted messages from {len(self.topics)} topics into [bold]{self.name}[/bold]"  # noqa: E501

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractTopic":
        """Return an ExtractTopic instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        return ExtractTopic(
            name=data["name"],
            topics=data["topics"],
            ffill=data.get("ffill", False),
        )

    def register(
        self,
        robolog_path: str | pathlib.Path,
        start_seconds: float | None,
        end_seconds: float | None,
    ) -> None:
        """Extract messages from topics and register the result as a DuckDB view.

        Args:
            robolog_path (str | pathlib.Path): Path to the robolog file or directory.
            start_seconds (float | None): When to start reading messages.
            end_seconds (float | None): When to stop reading messages.

        """
        reader = factory.make_topic_message_reader(robolog_path)
        dataset = reader.read(self.topics, start_seconds, end_seconds, self.ffill)
        relation = duckdb.from_arrow(dataset)
        duckdb.register(self.name, relation)
