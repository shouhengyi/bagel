"""An operator that applies a transformation on DuckDB views and return a new view."""

from typing import Any, Final

import duckdb
from pydantic import BaseModel

from src.command.run import validate


class TransformDataFrame(BaseModel):
    """An operator that applies a transformation on DuckDB views and return a new view."""

    # Name of the DuckDB view to register
    name: str

    # Keyword used in YAML to identify the operator
    YAML_KEYWORD: Final[str] = "transform_dataframe"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TransformDataFrame":
        """Return a TransformDataFrame instance from a dictionary."""
        validate.validate_snake_case(data["name"])
        match data:
            case {"name": name, "sql": sql}:
                return SqlTransformDataFrame(name=name, sql=sql)
            case _:
                raise ValueError(f"Failed to identify TransformDataFrame type: {data}")


class SqlTransformDataFrame(TransformDataFrame):
    """An operator that applies a SQL transformation on DuckDB views."""

    # SQL statement to apply
    sql: str

    @property
    def running_status(self) -> str:
        """Return the running status of the operator."""
        return f"Writing SQL query result into [bold]{self.name}[/bold]"

    @property
    def finished_status(self) -> str:
        """Return the finished status of the operator."""
        return f":white_check_mark: Wrote SQL query result into [bold]{self.name}[/bold]"

    def register(self) -> None:
        """Apply SQL statement and register the result as a DuckDB view."""
        relation = duckdb.sql(self.sql)
        duckdb.register(self.name, relation)
