"""MessageConverter implementation for Protobuf messages."""

from typing import Any

import pyarrow as pa
from google.protobuf import descriptor_pb2, json_format
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message import Message

from src.convert import converter
from src.convert.protobuf import cast


class TypeNameNotFoundError(Exception):
    """Raised when the specified type name is not found in the provided Protobuf schema."""


class MessageConverter(converter.MessageConverter):
    """Convert Protobuf messages to JSON-serializable dictionaries."""

    def __init__(self, type_name: str, file_descriptor_set_bytes: bytes) -> None:
        """Initialize a Protobuf MessageConverter.

        Args:
            type_name (str): A top-level Protobuf message type name (not full_name).
            file_descriptor_set_bytes (bytes): Serialized FileDescriptorSet bytes containing the
                protobuf schema.

        Raises:
            TypeNameNotFoundError: If the specified type name is not found in the provided schema.

        """
        self._type_name = type_name
        self._raw_schema = file_descriptor_set_bytes

        pool = DescriptorPool()
        file_descriptor_set = descriptor_pb2.FileDescriptorSet.FromString(file_descriptor_set_bytes)
        for file_descriptor in file_descriptor_set.file:
            pool.Add(file_descriptor)

        if message_descriptor := pool.FindMessageTypeByName(type_name):
            self._pa_struct = cast.cast_message_descriptor(message_descriptor)
        else:
            raise TypeNameNotFoundError(type_name)

    @property
    def type_name(self) -> str:
        """Return the type name of the Protobuf message."""
        return self._type_name

    @property
    def raw_schema(self) -> str | bytes:
        """Return the serialized FileDescriptorSet bytes."""
        return self._raw_schema

    @property
    def pa_struct(self) -> pa.StructType:
        """Return the pyarrow StructType that represents the Protobuf message schema."""
        return self._pa_struct

    def to_dict(self, message: Message) -> dict[str, Any]:
        """Convert a Protobuf message to a JSON-serializable dictionary."""
        return json_format.MessageToDict(
            message,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )
