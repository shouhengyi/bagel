"""MessageConverter implementation for ROS1 genpy.Message objects."""

from typing import Any

import pyarrow as pa

from src.convert import converter
from src.convert.ros1msg import cast, definition, parse

PRIMITIVE_TYPE = bool | int | float | str

FIELD_TYPE = PRIMITIVE_TYPE | object  # use `object` to avoid importing genpy


class MessageConverter(converter.MessageConverter):
    """Convert ROS1 genpy.Message objects to JSON-serializable dictionaries."""

    def __init__(self, type_name: str, ros1msg_string: str) -> None:
        """Initialize a ROS1 MessageConverter.

        Args:
            type_name (str): ROS1 message type name (e.g., 'std_msgs/Header').
            ros1msg_string (str): A ROS1 .msg definition string. Accessible via the `_full_text`
                attribute of genpy.Message objects.

        """
        self._type_name = type_name
        self._raw_schema = ros1msg_string
        self._main, self._dependencies = parse.parse(ros1msg_string)
        self._pa_struct = cast.to_pa_struct(self._main, self._dependencies)

    @property
    def type_name(self) -> str:
        """Return the type name of the genpy.Message."""
        return self._type_name

    @property
    def raw_schema(self) -> str | bytes:
        """Return the ROS1 .msg definition string."""
        return self._raw_schema

    @property
    def pa_struct(self) -> pa.StructType:
        """Return the pyarrow StructType that represents the genpy.Message schema."""
        return self._pa_struct

    def to_dict(self, message: object) -> dict[str, Any]:
        """Convert a genpy.Message to a JSON-serializable dictionary."""
        return {
            field.name: self._field_to_json_serializable(
                getattr(message, field.name), field, self._dependencies
            )
            for field in self._main.fields
        }

    def _field_to_json_serializable(
        self,
        field_value: FIELD_TYPE | list[FIELD_TYPE],
        field_struct: definition.Field,
        dependencies: dict[str, definition.Struct],
    ) -> PRIMITIVE_TYPE | list[PRIMITIVE_TYPE] | dict[str, Any]:
        if isinstance(field_struct, definition.Constant):
            return field_struct.value

        if isinstance(field_struct, definition.BuiltInField) and field_struct.type_ in (
            "time",
            "duration",
        ):
            if field_struct.is_array:
                return [{"secs": value.secs, "nsec": value.nsecs} for value in field_value]
            else:
                return {"secs": field_value.secs, "nsec": field_value.nsecs}

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
