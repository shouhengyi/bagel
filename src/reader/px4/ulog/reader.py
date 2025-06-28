"""Base class for PX4 .ulog readers."""

import heapq
import pathlib
from collections.abc import Iterator
from typing import Any

from pyulog import core

from src.reader import reader
from src.reader.px4.ulog.metadata import extract_metadata


class ULogReader(reader.Reader):
    """Base class for PX4 .ulog readers."""

    def __init__(self, robolog_path: str | pathlib.Path, use_cache: bool = True) -> None:
        """Initialize the ULogReader."""
        super().__init__(robolog_path, use_cache)

        self._metadata = extract_metadata(self.path)
        self._ulog = core.ULog(str(self.path), parse_header_only=False)

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        return self._metadata

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        return self.path.stat().st_size

    @property
    def total_message_count(self) -> int:
        """Return the total number of messages in the robolog."""
        total = 0
        for topic_data in self._ulog.data_list:
            if topic_data.data:
                first_field = next(iter(topic_data.data))
                total += len(topic_data.data[first_field])
        return total

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
