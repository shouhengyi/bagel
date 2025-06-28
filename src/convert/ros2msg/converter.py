"""MessageConverter implementation for ROS2 messages."""

from typing import Any

import pyarrow as pa

from src.convert import converter
from src.convert.ros2msg import cast, definition, parse

PRIMITIVE_TYPE = bool | int | float | str

FIELD_TYPE = PRIMITIVE_TYPE | Any


class MessageConverter(converter.MessageConverter):
    """Convert ROS2 messages to JSON-serializable dictionaries."""

    def __init__(self, type_name: str, ros2msg_string: str) -> None:
        """Initialize a ROS2 MessageConverter.

        Args:
            type_name (str): ROS2 message type name (e.g., 'std_msgs/Header').
            ros2msg_string (str): A ROS2 .msg definition string. Accessible via the `data` attribute
                of mcap.records.Schema objects when `encoding='ros2msg'`.

        """
        self._type_name = type_name
        self._raw_schema = ros2msg_string
        self._main, self._dependencies = parse.parse(self._raw_schema)
        self._pa_struct = cast.to_pa_struct(self._main, self._dependencies)

    @property
    def type_name(self) -> str:
        """Return the type name of the ROS2 message."""
        return self._type_name

    @property
    def raw_schema(self) -> str | bytes:
        """Return the ROS2 .msg definition string."""
        return self._raw_schema

    @property
    def pa_struct(self) -> pa.StructType:
        """Return the pyarrow StructType that represents the ROS2 message schema."""
        return self._pa_struct

    def to_dict(self, message: object) -> dict[str, Any]:
        """Convert a ROS2 message to a JSON-serializable dictionary."""
        fields = {}
        for field in self._main.fields:
            if isinstance(field, definition.Constant):
                fields[field.name] = field.value
            else:
                fields[field.name] = self._field_to_json_serializable(
                    getattr(message, field.name), field, self._dependencies
                )
        return fields

    def _field_to_json_serializable(
        self,
        field_value: FIELD_TYPE | list[FIELD_TYPE],
        field_struct: definition.Field,
        dependencies: dict[str, definition.Struct],
    ) -> PRIMITIVE_TYPE | list[PRIMITIVE_TYPE] | dict[str, Any]:
        if isinstance(field_struct, definition.Constant):
            return field_struct.value

        match field_struct:
            case definition.BuiltInField():
                return field_value

            case definition.ComplexField(is_array=False):
                return {
                    child.name: self._field_to_json_serializable(
                        getattr(field_value, child.name), child, dependencies
                    )
                    for child in dependencies[field_struct.type_].fields
                }

            case definition.ComplexField(is_array=True):
                result = []
                for value in field_value:
                    result.append(
                        {
                            child.name: self._field_to_json_serializable(
                                getattr(value, child.name), child, dependencies
                            )
                            for child in dependencies[field_struct.type_].fields
                        }
                    )
                return result
