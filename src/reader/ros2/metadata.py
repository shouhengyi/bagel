"""Convert a rosbag2_py.BagMetadata object to a JSON-serializable dictionary."""

import functools
import pathlib
from typing import Any

import rosbag2_py

from src.reader.metadata import find_primitives

PY_PRIMITIVE_TYPES = (bool, int, float, str, bytes, type(None))


def _file_information(data: rosbag2_py.FileInformation) -> dict[str, Any]:
    """Convert a FileInformation object to a JSON-serializable dictionary."""
    required = {
        "path": data.path,
        "starting_time_seconds": data.starting_time.nanoseconds / 1e9,
        "duration_seconds": data.duration.total_seconds(),
        "message_count": data.message_count,
    }
    return {**find_primitives(data), **required}


def _topic_metadata(data: rosbag2_py.TopicMetadata) -> dict[str, Any]:
    """Convert a TopicMetadata object to a JSON-serializable dictionary."""
    required = {
        "name": data.name,
        "type": data.type,
        "serialization_format": data.serialization_format,
    }
    return {**find_primitives(data), **required}


def _topic_information(data: rosbag2_py.TopicInformation) -> dict[str, Any]:
    """Convert a TopicInformation object to a JSON-serializable dictionary."""
    required = {
        "message_count": data.message_count,
        "topic_metadata": _topic_metadata(data.topic_metadata),
    }
    return {**find_primitives(data), **required}


def _bag_metadata(data: rosbag2_py.BagMetadata) -> dict[str, Any]:
    """Convert a BagMetadata object to a JSON-serializable dictionary.

    This function manually converts a `rosbag2_py.BagMetadata` object into a
    dictionary suitable for JSON serialization. This approach is necessary as there
    is no native direct serialization support for this object type.

    The structure of the returned dictionary adheres to the BagMetadata schema
    defined in ROS2 Humble. Specifically, it reflects the fields exposed
    by rosbag2_py as found in the `_storage.cpp` implementation:
    `https://github.com/ros2/rosbag2/blob/humble/rosbag2_py/src/rosbag2_py/_storage.cpp#L184`

    Future ROS2 distributions (beyond Humble) are assumed to maintain
    compatibility regarding existing field types and presence. While new
    fields may be introduced, this function aims to include them in the
    output dictionary if they are of Python primitive types, i.e., complex
    fields will be ignored.

    """
    required = {
        "version": data.version,
        "bag_size": data.bag_size,
        "storage_identifier": data.storage_identifier,
        "relative_file_paths": data.relative_file_paths,
        "files": [_file_information(file_info) for file_info in data.files],
        "duration_seconds": data.duration.nanoseconds / 1e9,
        "starting_time_seconds": data.starting_time.nanoseconds / 1e9,
        "message_count": data.message_count,
        "topics_with_message_count": [
            _topic_information(topic_info) for topic_info in data.topics_with_message_count
        ],
        "compression_format": data.compression_format,
        "compression_mode": data.compression_mode,
    }
    return {**find_primitives(data), **required}


@functools.lru_cache(maxsize=128)
def extract_metadata(
    robolog_path: str | pathlib.Path, storage_id: str | None = None
) -> dict[str, Any]:
    """Return metadata from a ROS2 bag file as a JSON-serializable dictionary.

    Args:
        robolog_path (str | pathlib.Path): Path to the ROS2 bag file or directory.
        storage_id (str | None): Storage identifier for the bag, e.g., "sqlite3" or "mcap".
            If None, it infers the storage ID. Otherwise, only the specified storage ID is allowed.

    Returns:
        dict[str, Any]: Robolog's metadata as a JSON-serializable dictionary.

    """
    return _bag_metadata(rosbag2_py.Info().read_metadata(str(robolog_path), storage_id or ""))
