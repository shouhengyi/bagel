"""An operator that extracts messages of a particular type in a robolog."""

import pathlib
from typing import Any, Final

import duckdb
from pydantic import BaseModel

from src.command.run import validate
from src.reader import factory


class ExtractType(BaseModel):
    """An operator that extracts messages of a particular type in a robolog."""

    # Name of the DuckDB view to register
    name: str

    # Message type to extract
    type_name: str

    # List of topics to exclude from the extraction
    exclude_topics: list[str]

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "extract_type"

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Extracting messages of '{self.type_name}' into [bold]{self.name}[/bold]"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Extracted messages of '{self.type_name}' into [bold]{self.name}[/bold]"  # noqa: E501

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractType":
        """Return an ExtractType instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        return ExtractType(
            name=data["name"],
            type_name=data["type_name"],
            exclude_topics=data.get("exclude_topics", []),
        )

    def register(
        self,
        robolog_path: str | pathlib.Path,
        start_seconds: float | None,
        end_seconds: float | None,
    ) -> None:
        """Extract messages of a particular type and register the result as a DuckDB view.

        Args:
            robolog_path (str | pathlib.Path): Path to the robolog file or directory.
            start_seconds (float | None): When to start reading messages.
            end_seconds (float | None): When to stop reading messages.

        """
        reader = factory.make_type_message_reader(robolog_path)
        dataset = reader.read(
            self.type_name, start_seconds, end_seconds, exclude_topics=self.exclude_topics
        )
        relation = duckdb.from_arrow(dataset)
        duckdb.register(self.name, relation)
