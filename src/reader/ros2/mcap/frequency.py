"""Calculate the frequency of messages in a ROS2 .mcap bag by topic."""

import pathlib
from collections.abc import Iterator

import pyarrow as pa
from mcap.reader import make_reader

from settings import settings
from src.reader.frequency import TopicFrequencyReader
from src.reader.ros2.reader import Ros2Reader


class TopicFrequencyReader(TopicFrequencyReader, Ros2Reader):
    """Calculate the frequency of messages in a ROS2 .mcap bag by topic."""

    def __init__(self, robolog_path: str | pathlib.Path, use_cache: bool = True) -> None:
        """Initialize the TopicFrequencyReader."""
        super().__init__(robolog_path, storage_id="mcap", use_cache=use_cache)

    def _iter_record_batches(
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        schema: pa.Schema,
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        batch_size = settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT
        batch = {column: [] for column in schema.names}
        latest = {topic: None for topic in topics}

        for mcap_file in self.metadata["relative_file_paths"]:
            with open(self.path / mcap_file, "rb") as stream:
                messages = make_reader(stream).iter_messages(
                    topics,
                    start_seconds * 1e9 if start_seconds else None,
                    end_seconds * 1e9 if end_seconds else None,
                )

                for _, channel, message in messages:
                    timestamp_seconds = message.log_time / 1e9
                    record = {colname: None for colname in schema.names}
                    record[settings.ROBOLOG_ID_COLUMN_NAME] = self.robolog_id
                    record[settings.TIMESTAMP_SECONDS_COLUMN_NAME] = timestamp_seconds
                    if latest[channel.topic] is not None:
                        record[channel.topic] = timestamp_seconds - latest[channel.topic]
                    latest[channel.topic] = timestamp_seconds

                    for column, value in record.items():
                        batch[column].append(value)

                    if len(batch[settings.ROBOLOG_ID_COLUMN_NAME]) >= batch_size:
                        record_batch = pa.RecordBatch.from_pydict(batch, schema=schema)
                        batch_size = self._estimate_record_batch_size_count(record_batch)
                        batch = {column: [] for column in schema.names}
                        yield record_batch

        if batch[settings.ROBOLOG_ID_COLUMN_NAME]:
            yield pa.RecordBatch.from_pydict(batch, schema=schema)
