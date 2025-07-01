"""Read messages from a ROS1 .bag file by topic."""

from collections.abc import Iterator

import genpy
import pyarrow as pa
import rosbag

from settings import settings
from src.convert.converter import MessageConverter
from src.reader.ros1.bag.reader import BagReader
from src.reader.topic import TopicMessageReader


class TopicMessageReader(TopicMessageReader, BagReader):
    """Read messages from a ROS1 .bag file by topic."""

    def _iter_record_batches(  # noqa: PLR0913
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        ffill: bool,
        schema: pa.Schema,
        converters: dict[str, MessageConverter],
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        with rosbag.Bag(self.path, allow_unindexed=self._allow_unindexed) as bag:
            messages = bag.read_messages(
                topics,
                genpy.Time.from_sec(start_seconds) if start_seconds else None,
                genpy.Time.from_sec(end_seconds) if end_seconds else None,
            )

            batch_size = settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT
            batch = {column: [] for column in schema.names}
            record = {column: None for column in schema.names}

            for topic, message, timestamp in messages:
                if not ffill:
                    record = {column: None for column in schema.names}
                record[settings.ROBOLOG_ID_COLUMN_NAME] = self.robolog_id
                record[settings.TIMESTAMP_SECONDS_COLUMN_NAME] = timestamp.to_sec()
                record[topic] = converters[topic].to_dict(message)

                for column, value in record.items():
                    batch[column].append(value)

                if len(batch[settings.ROBOLOG_ID_COLUMN_NAME]) >= batch_size:
                    record_batch = pa.RecordBatch.from_pydict(batch, schema=schema)
                    batch_size = self._estimate_record_batch_size_count(record_batch)
                    batch = {column: [] for column in schema.names}
                    yield record_batch

            if batch[settings.ROBOLOG_ID_COLUMN_NAME]:
                yield pa.RecordBatch.from_pydict(batch, schema=schema)
