"""Base class for ROS2 bag readers."""

import pathlib
from typing import Any

import rosbag2_py

from src.reader import reader
from src.reader.ros2 import metadata


class Ros2Reader(reader.Reader):
    """Base class for ROS2 bag readers."""

    def __init__(self, robolog_path: str | pathlib.Path, storage_id: str, use_cache: bool) -> None:
        """Initialize the Ros2Reader."""
        super().__init__(robolog_path, use_cache)

        self._storage_options = rosbag2_py.StorageOptions(uri=str(self.path), storage_id=storage_id)
        self._metadata = metadata.extract_metadata(self.path, self._storage_options.storage_id)

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        return self._metadata

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        return self.metadata["bag_size"]

    @property
    def topics(self) -> list[str]:
        """Return a list of topics in the robolog."""
        return list(
            set(
                topic_info["topic_metadata"]["name"]
                for topic_info in self.metadata["topics_with_message_count"]
            )
        )

    @property
    def type_names(self) -> dict[str, str]:
        """Return a mapping of topic names to their message type names."""
        return {
            topic_info["topic_metadata"]["name"]: topic_info["topic_metadata"]["type"]
            for topic_info in self.metadata["topics_with_message_count"]
        }

    @property
    def message_counts(self) -> dict[str, int]:
        """Return a mapping of topic names to their message counts."""
        return {
            topic_info["topic_metadata"]["name"]: topic_info["message_count"]
            for topic_info in self.metadata["topics_with_message_count"]
        }
