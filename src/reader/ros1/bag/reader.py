"""Base class for ROS1 .bag file readers."""

import pathlib
from typing import Any

import rosbag
import yaml

from src.reader import reader


class BagReader(reader.Reader):
    """Base class for ROS1 .bag file readers."""

    def __init__(
        self, robolog_path: str | pathlib.Path, use_cache: bool = True, allow_unindexed: bool = True
    ) -> None:
        """Initialize the BagReader."""
        super().__init__(robolog_path, use_cache)

        self._allow_unindexed = allow_unindexed
        with rosbag.Bag(self.path, allow_unindexed=self._allow_unindexed) as bag:
            self._metadata = yaml.safe_load(bag._get_yaml_info())

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        return self._metadata

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        return self.metadata["size"]

    @property
    def message_count(self) -> int:
        """Return the total number of messages in the robolog."""
        return self.metadata["messages"]

    @property
    def topics(self) -> list[str]:
        """Return a list of topics in the robolog."""
        return [info["topic"] for info in self.metadata["topics"]]

    @property
    def type_names(self) -> dict[str, str]:
        """Return a mapping of topic names to their message type names."""
        return {info["topic"]: info["type"] for info in self.metadata["topics"]}
