"""Base class for ROS1 .bag file readers."""

import pathlib
from collections.abc import Iterator
from typing import Any

import rosbag
import yaml

from src.reader import reader

LOGGING_MESSAGE_TYPE_NAME = "rosgraph_msgs/Log"


class LoggingMessage(reader.LoggingMessage):
    """Logging message in a ROS1 .bag file."""

    numeric_level: int
    topic: str
    name: str
    file: str
    function: str
    line: int

    def to_dict(self) -> dict[str, Any]:
        """Convert the logging message to a dictionary."""
        return {
            **super().to_dict(),
            "numeric_level": self.numeric_level,
            "topic": self.topic,
            "name": self.name,
            "file": self.file,
            "function": self.function,
            "line": self.line,
        }


class BagReader(reader.Reader):
    """Base class for ROS1 .bag file readers."""

    def __init__(
        self, robolog_path: str | pathlib.Path, use_cache: bool = True, allow_unindexed: bool = True
    ) -> None:
        """Initialize the BagReader."""
        super().__init__(robolog_path, use_cache)

        self._bag = rosbag.Bag(robolog_path, allow_unindexed=allow_unindexed)
        self._metadata = yaml.safe_load(self._bag._get_yaml_info())

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        return self._metadata

    @property
    def start_seconds(self) -> float:
        """Return robolog start time in seconds."""
        self._bag.get_start_time()

    @property
    def end_seconds(self) -> float:
        """Return robolog end time in seconds."""
        self._bag.get_end_time()

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        return self.metadata["size"]

    @property
    def topics(self) -> list[str]:
        """Return a list of topics in the robolog."""
        return [info["topic"] for info in self.metadata["topics"]]

    @property
    def type_names(self) -> dict[str, str]:
        """Return a mapping of topic names to their message type names."""
        return {info["topic"]: info["type"] for info in self.metadata["topics"]}

    @property
    def message_counts(self) -> dict[str, int]:
        """Return a mapping of topic names to their message counts."""
        return {info["topic"]: info["messages"] for info in self.metadata["topics"]}

    @property
    def logging_messages(self) -> Iterator[LoggingMessage]:
        """Iterate over logging messages in the robolog."""
        topics = [
            topic
            for topic, type_name in self.type_names.items()
            if type_name == LOGGING_MESSAGE_TYPE_NAME
        ]

        if not topics:
            return

        for topic, message, timestamp in self._bag.read_messages(topics=topics):
            level = {
                1: "DEBUG",
                2: "INFO",
                4: "WARN",
                8: "ERROR",
                16: "FATAL",
            }.get(message.level, "UNKNOWN")

            yield LoggingMessage(
                robolog_id=self.robolog_id,
                timestamp_seconds=timestamp.to_sec(),
                level=level,
                message=message.msg,
                numeric_level=message.level,
                topic=topic,
                name=message.name,
                file=message.file,
                function=message.function,
                line=message.line,
            )
