"""Read messages from a ROS2 .db3 bag by topic."""

import pathlib
from collections.abc import Iterator

import pyarrow as pa
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

from settings import settings
from src.convert.converter import MessageConverter
from src.reader.ros2.reader import Ros2Reader
from src.reader.topic import TopicMessageReader


class TopicMessageReader(TopicMessageReader, Ros2Reader):
    """Read messages from a ROS2 .db3 bag by topic."""

    def __init__(self, robolog_path: str | pathlib.Path, use_cache: bool = True) -> None:
        """Initialize the TopicMessageReader."""
        super().__init__(robolog_path, storage_id="sqlite3", use_cache=use_cache)

    def _iter_record_batches(  # noqa: PLR0913
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        asof_join: bool,
        schema: pa.Schema,
        converters: dict[str, MessageConverter],
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        reader = rosbag2_py.SequentialReader()
        reader.open(self._storage_options, rosbag2_py.ConverterOptions("", ""))
        reader.set_filter(rosbag2_py.StorageFilter(topics))
        if start_seconds is not None:
            reader.seek(int(start_seconds * 1e9))

        batch_size = settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT
        batch = {column: [] for column in schema.names}
        record = {column: None for column in schema.names}

        while reader.has_next():
            topic, serialized_message, nanoseconds = reader.read_next()
            timestamp_seconds = nanoseconds / 1e9
            if end_seconds is not None and timestamp_seconds > end_seconds:
                break

            if not asof_join:
                record = {column: None for column in schema.names}
            record[settings.ROBOLOG_ID_COLUMN_NAME] = self.robolog_id
            record[settings.TIMESTAMP_SECONDS_COLUMN_NAME] = timestamp_seconds
            record[topic] = converters[topic].to_dict(
                deserialize_message(serialized_message, get_message(self.type_names[topic]))
            )

            for column, value in record.items():
                batch[column].append(value)

            if len(batch[settings.ROBOLOG_ID_COLUMN_NAME]) >= batch_size:
                record_batch = pa.RecordBatch.from_pydict(batch, schema=schema)
                batch_size = self._estimate_record_batch_size_count(record_batch)
                batch = {column: [] for column in schema.names}
                yield record_batch

        if hasattr(reader, "close"):  # The `close` method was added since Jazzy
            reader.close()

        if batch[settings.ROBOLOG_ID_COLUMN_NAME]:
            yield pa.RecordBatch.from_pydict(batch, schema=schema)
