"""Base class for PX4 .ulg readers."""

import heapq
import pathlib
from collections.abc import Iterator
from typing import Any

from pyulog import core

from src.reader import reader
from src.reader.metadata import find_primitives


class LoggingMessage(reader.LoggingMessage):
    """Logging message in a PX4 .ulg."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the logging message to a dictionary."""
        numeric_level = {
            "DEBUG": 7,
            "INFO": 6,
            "NOTICE": 5,
            "WARNING": 4,
            "ERROR": 3,
            "CRITICAL": 2,
            "ALERT": 1,
            "EMERGENCY": 0,
        }.get(self.level, None)
        return {
            **super().to_dict(),
            "numeric_level": numeric_level,
        }


def _start_and_end_seconds_from_gps(ulog: core.ULog) -> tuple[float | None, float | None]:
    gps_data_list = [data for data in ulog.data_list if data.name == "vehicle_gps_position"]
    gps_data_list = sorted(gps_data_list, key=lambda x: x.multi_id)
    start_timestamp_seconds = gps_data_list[0].data["time_utc_usec"][0] / 1e6
    end_timestamp_seconds = gps_data_list[-1].data["time_utc_usec"][-1] / 1e6
    return start_timestamp_seconds, end_timestamp_seconds


def _metadata_from_ulog(ulog: core.ULog) -> dict[str, Any]:
    # ULog must be initialized with `parse_header_only=False` to include all topics.
    return {
        "start_timestamp_seconds": ulog.start_timestamp / 1e6,
        "last_timestamp_seconds": ulog.last_timestamp / 1e6,
        "msg_info_dict": ulog.msg_info_dict,
        "msg_info_multiple_dict": ulog.msg_info_multiple_dict,
        "initial_parameters": ulog.initial_parameters,
        "changed_parameters": ulog.changed_parameters,
        "message_formats": {k: find_primitives(v) for k, v in ulog.message_formats.items()},
        "logged_messages": [find_primitives(item) for item in ulog.logged_messages],
        "logged_messages_tagged": {
            k: find_primitives(v) for k, v in ulog.logged_messages_tagged.items()
        },
        "dropouts": [find_primitives(item) for item in ulog.dropouts],
        "has_data_appended": ulog.has_data_appended,
        "file_corruption": ulog.file_corruption,
        "has_default_parameters": ulog.has_default_parameters,
    }


class ULogReader(reader.Reader):
    """Base class for PX4 .ulg readers."""

    def __init__(self, robolog_path: str | pathlib.Path, use_cache: bool = True) -> None:
        """Initialize the ULogReader."""
        super().__init__(robolog_path, use_cache)
        self._ulog = core.ULog(str(robolog_path), parse_header_only=False)
        self._metadata = _metadata_from_ulog(self._ulog)

        try:
            self._start_seconds, self._end_seconds = _start_and_end_seconds_from_gps(self._ulog)
        except Exception:
            self._start_seconds = self._ulog.start_timestamp / 1e6
            self._end_seconds = self._ulog.last_timestamp / 1e6

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        return self._metadata

    @property
    def start_seconds(self) -> float:
        """Return robolog start time in seconds."""
        return self._start_seconds

    @property
    def end_seconds(self) -> float:
        """Return robolog end time in seconds."""
        return self._end_seconds

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        return self.path.stat().st_size

    @property
    def topics(self) -> list[str]:
        """Return a list of topics in the robolog."""
        return [f"{topic_data.name}_{topic_data.multi_id}" for topic_data in self._ulog.data_list]

    @property
    def type_names(self) -> dict[str, str]:
        """Return a mapping of topic names to their message type names."""
        return {
            f"{topic_data.name}_{topic_data.multi_id}": topic_data.name
            for topic_data in self._ulog.data_list
        }

    @property
    def message_counts(self) -> dict[str, int]:
        """Return a mapping of topic names to their message counts."""
        counts = {}
        for topic_data in self._ulog.data_list:
            topic_name = f"{topic_data.name}_{topic_data.multi_id}"
            first_field = next(iter(topic_data.data))
            counts[topic_name] = len(topic_data.data[first_field])
        return counts

    @property
    def logging_messages(self) -> Iterator[LoggingMessage]:
        """Iterate over logging messages in the robolog."""
        for message in self._ulog.logged_messages:
            yield LoggingMessage(
                robolog_id=self.robolog_id,
                timestamp_seconds=message.timestamp / 1e6,
                level=message.log_level_str(),
                message=message.message,
            )

    def _iter_messages(
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        timestamps_only: bool,
    ) -> Iterator[tuple[float, str, dict[str, Any] | None]]:
        """Iterate over messages for the specified topics and time range.

        Args:
            topics (list[str]): A list of topic names to read messages from. For PX4 ULog, it takes
                the form of `topic_name_<multi_id>`, where `multi_id` is an integer.
            start_seconds (float | None): When to start reading messages.
            end_seconds (float | None): When to stop reading messages.
            timestamps_only (bool): If True, only return timestamps and topic names without message.

        Yields:
            Iterator[tuple[float, str, dict[str, Any] | None]]: A generator that yields tuples
                containing the timestamp in seconds, topic name, and message (or None if
                `timestamps_only` is True).

        """
        timestamps_and_indices, datasets = {}, {}
        for topic in topics:
            multi_id = int(topic.split("_")[-1])
            dataset = self._ulog.get_dataset(self.type_names[topic], multi_id)
            timestamp_field = dataset.field_data[dataset.timestamp_idx].field_name

            timestamp_milliseconds = dataset.data[timestamp_field]
            condition = [True] * len(timestamp_milliseconds)
            if start_seconds is not None:
                condition &= timestamp_milliseconds >= start_seconds * 1e6
            if end_seconds is not None:
                condition &= timestamp_milliseconds <= end_seconds * 1e6

            timestamps_and_indices[topic] = iter(
                [
                    (self.start_seconds + timestamp_milliseconds[i] / 1e6, i)
                    for i, c in enumerate(condition)
                    if c
                ]
            )
            datasets[topic] = dataset

        heap = []
        for topic, iterator in timestamps_and_indices.items():
            timestamp, i = next(iterator)
            heapq.heappush(heap, (timestamp, topic, i))

        while heap:
            timestamp, topic, i = heapq.heappop(heap)

            message = None
            if not timestamps_only:
                message = {}
                for field, values in datasets[topic].data.items():
                    message[field] = values[i]

            yield timestamp, topic, message

            try:
                next_timestamp, next_i = next(timestamps_and_indices[topic])
                heapq.heappush(heap, (next_timestamp, topic, next_i))
            except StopIteration:
                continue
