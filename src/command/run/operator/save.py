"""An operator that saves a DuckDB view to disk."""

import pathlib
from datetime import datetime
from enum import Enum
from typing import Final

import duckdb

from settings import settings
from src import robolog
from src.command.run import validate
from src.command.run.operator.base import Operator
from src.reader import factory


class FileExtension(Enum):
    """Enum for supported file extensions."""

    PARQUET = "parquet"
    CSV = "csv"
    JSONL = "jsonl"


class SaveDataFrame(Operator):
    """An operator that saves a DuckDB view to disk."""

    # Name of the DuckDB view to save
    name: str

    # Keyword used in YAML to identify the operator
    YAML_KEY: Final[str] = "save_dataframe"

    # Path to the saved file. Used for status messages
    _saved_file_path: pathlib.Path

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Saving **{self.name}** to disk"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":floppy_disk: Saved **{self.name}** to {self._saved_file_path}"

    @staticmethod
    def from_name(data: str) -> "SaveDataFrame":
        """Return a SaveDataFrame instance from a DataFrame name."""
        validate.validate_snake_case(data)
        return SaveDataFrame(name=data)

    def write(
        self,
        robolog_path: str | pathlib.Path,
        start_seconds: float | None,
        end_seconds: float | None,
        ext: FileExtension = FileExtension.PARQUET,
        dry_run: bool = False,
    ) -> pathlib.Path:
        """Write the DuckDB view to disk and return the file path."""
        reader = factory.make_topic_message_reader(robolog_path)
        datestr = datetime.fromtimestamp(reader.start_seconds).strftime("%Y-%m-%d")
        start_seconds = start_seconds or reader.start_seconds
        end_seconds = end_seconds or reader.end_seconds

        file_path = (
            pathlib.Path(settings.DATASET_DIRECTORY)
            / self.name
            / f"datestr={datestr}"
            / f"{robolog.snippet_name(robolog_path, start_seconds, end_seconds)}.{ext.value}"
        )

        try:
            relation = duckdb.view(self.name)
            if not dry_run:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                match ext:
                    case FileExtension.PARQUET:
                        relation.write_parquet(str(file_path))
                    case FileExtension.CSV:
                        relation.write_csv(str(file_path))
                    case FileExtension.JSONL:
                        duckdb.sql(f"COPY relation TO '{file_path!s}' (FORMAT 'JSON')")
                    case _:
                        raise ValueError(f"Unsupported disk format: {ext}")
            self._saved_file_path = file_path

        except Exception as e:
            self._saved_file_path = None
            if not dry_run:
                file_path.unlink(missing_ok=True)
            raise e
