"""An operator that saves a DuckDB view to disk."""

import pathlib
from enum import Enum
from typing import Final

import duckdb
from pydantic import BaseModel

from settings import settings
from src import robolog
from src.command.extract import validate


class FileExtension(Enum):
    """Enum for supported file extensions."""

    PARQUET = "parquet"
    CSV = "csv"
    JSONL = "jsonl"


class SaveDataFrame(BaseModel):
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
        return f"Saving [bold]{self.name}[/bold] to disk"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":floppy_disk: Saved [bold]{self.name}[/bold] to {self._saved_file_path}"

    @staticmethod
    def from_dict(data: str) -> "SaveDataFrame":
        """Return a SaveDataFrame instance from a dictionary."""
        validate.validate_snake_case(data)
        return SaveDataFrame(name=data)

    def write(
        self,
        robolog_path: str | pathlib.Path,
        start_seconds: float | None,
        end_seconds: float | None,
        ext: FileExtension = FileExtension.PARQUET,
    ) -> pathlib.Path:
        """Write the DuckDB view to disk and return the file path."""
        file_path = (
            pathlib.Path(settings.STORAGE_DIRECTORY)
            / self.name
            / f"datestr={robolog.datestr(robolog_path)}"
            / f"{robolog.snippet_name(robolog_path, start_seconds, end_seconds)}.{ext.value}"
        )

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            relation = duckdb.view(self.name)
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
            file_path.unlink(missing_ok=True)
            raise e
