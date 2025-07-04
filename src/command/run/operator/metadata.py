"""An operator that extracts metadata from a robolog."""

import pathlib
from typing import Any, Final

import duckdb
import pandas as pd

from src.command.run import validate
from src.command.run.operator.base import Operator
from src.reader import factory


class ExtractMetadata(Operator):
    """An operator that extracts metadata from a robolog."""

    # Name of the DuckDB view to register
    name: str

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "extract_metadata"

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Extracting metadata into **{self.name}**"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Extracted metadata into **{self.name}**"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExtractMetadata":
        """Return an ExtractMetadata instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        return ExtractMetadata(name=data["name"])

    def register(
        self,
        robolog_path: str | pathlib.Path,
    ) -> None:
        """Extract metadata and register the result as a DuckDB view.

        Args:
            robolog_path (str | pathlib.Path): Path to the robolog file or directory.

        """
        reader = factory.make_topic_message_reader(robolog_path)
        record = {
            "robolog_id": reader.robolog_id,
            "start_seconds": reader.start_seconds,
            "end_seconds": reader.end_seconds,
            "duration_seconds": reader.duration_seconds,
            "path": str(reader.path),
            "size_bytes": reader.size_bytes,
            "total_message_count": reader.total_message_count,
            "topics": reader.topics,
            "metadata": reader.metadata,
        }
        relation = duckdb.from_df(pd.DataFrame([record]))
        duckdb.register(self.name, relation)
