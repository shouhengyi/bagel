"""MessageConverter implementation for PX4 ULog messages."""

from typing import Any

import pyarrow as pa

from src.convert import converter
from src.convert.px4ulog import cast


class MessageConverter(converter.MessageConverter):
    """Convert PX4 ULog messages to JSON-serializable dictionaries."""

    def __init__(self, type_name: str, yaml_string: str) -> None:
        """Initialize a PX4 ULog MessageConverter.

        Args:
            type_name (str): PX4 message type name (e.g., 'vehicle_local_position').
            yaml_string (str): A YAML string representing the message schema.

        """
        self._type_name = type_name
        self._raw_schema = yaml_string
        self._pa_struct = cast.to_pa_struct(yaml_string)

    @property
    def type_name(self) -> str:
        """Return the type name of the ULog message."""
        return self._type_name

    @property
    def raw_schema(self) -> str | bytes:
        """Return the ULog message definition string."""
        return self._raw_schema

    @property
    def pa_struct(self) -> pa.StructType:
        """Return the pyarrow StructType that represents the ULog message schema."""
        return self._pa_struct

    def to_dict(self, message: dict[str, Any]) -> dict[str, Any]:
        """Convert a ULog message to a JSON-serializable dictionary.

        The message should already be a dictionary with keys matching the schema.

        """
        return message
