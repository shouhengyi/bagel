"""Base reader classes for different reading patterns and robolog types."""

import pathlib
from typing import Any

import pyarrow as pa

from settings import settings
from src import robolog
from src.convert import factory
from src.convert.converter import MessageConverter


class TopicsNotFoundError(ValueError):
    """Raised when topics are not found in the robolog."""


class MessageTypeNotFoundError(ValueError):
    """Raised when a message type is not found in the robolog."""


class Reader:
    """Base class for reading data from a robolog."""

    def __init__(self, robolog_path: str | pathlib.Path, use_cache: bool) -> None:
        """Initialize the Reader.

        Args:
            robolog_path (str | pathlib.Path): The path to the robolog.
            use_cache (bool): If True, use cached result if available.

        """
        self._path = pathlib.Path(robolog_path).absolute()
        self._use_cache = use_cache
        self._robolog_id = robolog.generate_id(self.path)
        self._start_seconds, self._end_seconds = robolog.start_and_end_seconds(self.path)

    @property
    def robolog_id(self) -> str:
        """Return robolog UUID."""
        return self._robolog_id

    @property
    def start_seconds(self) -> float:
        """Return robolog start time in seconds.

        Note that this timestamp might be relative to system boot time rather than the Unix epoch.

        """
        return self._start_seconds

    @property
    def end_seconds(self) -> float:
        """Return robolog end time in seconds.

        Note that this timestamp might be relative to system boot time rather than the Unix epoch.

        """
        return self._end_seconds

    @property
    def duration_seconds(self) -> float:
        """Return robolog duration in seconds."""
        return self.end_seconds - self.start_seconds

    @property
    def path(self) -> pathlib.Path:
        """Return the absolute path of the robolog."""
        return self._path

    @property
    def total_message_count(self) -> int:
        """Return the total number of messages in the robolog."""
        return sum(self.message_counts.values())

    @property
    def metadata(self) -> dict[str, Any]:
        """Return robolog metadata as a JSON-serializable dictionary."""
        raise NotImplementedError()

    @property
    def size_bytes(self) -> int:
        """Return robolog size in bytes."""
        raise NotImplementedError()

    @property
    def topics(self) -> list[str]:
        """Return a list of topics in the robolog."""
        raise NotImplementedError()

    @property
    def type_names(self) -> dict[str, str]:
        """Return a mapping of topic names to their message type names."""
        raise NotImplementedError()

    @property
    def message_counts(self) -> dict[str, int]:
        """Return a mapping of topic names to their message counts."""
        raise NotImplementedError()

    def _raise_if_missing_topics(self, topics: list[str]) -> None:
        """Raise if the specified topics are not found in the robolog."""
        missing = list(set(topics) - set(self.topics))
        if missing:
            raise TopicsNotFoundError(missing)

    def _raise_if_missing_type(self, type_name: str) -> None:
        """Raise if the specified message type is not found in the robolog."""
        if type_name not in set(self.type_names.values()):
            raise MessageTypeNotFoundError(type_name)

    def _converters(self, topics: list[str]) -> dict[str, MessageConverter]:
        """Return message converters for the specified topics."""
        return {
            topic: factory.make_converter(self.path, self.type_names[topic]) for topic in topics
        }

    def _estimate_record_batch_size_count(self, record_batch: pa.RecordBatch) -> int:
        """Estimate the number of rows that can fit in a record batch."""
        estimate = int(
            (settings.ARROW_RECORD_BATCH_SIZE_BYTES / record_batch.nbytes) * record_batch.num_rows
        )
        return max(estimate, settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT)
