"""Read messages from a ROS2 .mcap bag by message type."""

import pathlib
from collections.abc import Iterator

import pyarrow as pa
from mcap import decoder
from mcap.reader import make_reader

from settings import settings
from src.convert.converter import MessageConverter
from src.reader.ros2.reader import Ros2Reader
from src.reader.type import TypeMessageReader


class TypeMessageReader(TypeMessageReader, Ros2Reader):
    """Read messages from a ROS2 .mcap bag by message type."""

    def __init__(
        self,
        robolog_path: str | pathlib.Path,
        use_cache: bool = True,
        decoder_factories: list[decoder.DecoderFactory] | None = None,
    ) -> None:
        """Initialize the TypeMessageReader."""
        super().__init__(robolog_path, storage_id="mcap", use_cache=use_cache)

        if decoder_factories is None:
            from mcap_protobuf.decoder import DecoderFactory as ProtobufDecoderFactory
            from mcap_ros1.decoder import DecoderFactory as Ros1DecoderFactory
            from mcap_ros2.decoder import DecoderFactory as Ros2DecoderFactory
            # ... more factories can be added here once available.

            decoder_factories = [
                Ros1DecoderFactory(),
                Ros2DecoderFactory(),
                ProtobufDecoderFactory(),
            ]

        self._decoder_factories = decoder_factories

    def _iter_record_batches(
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        schema: pa.Schema,
        converter: MessageConverter,
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        batch_size = settings.MIN_ARROW_RECORD_BATCH_SIZE_COUNT
        batch = {colname: [] for colname in schema.names}

        for mcap_file in self.metadata["relative_file_paths"]:
            with open(self.path / mcap_file, "rb") as stream:
                reader = make_reader(stream, decoder_factories=self._decoder_factories)
                messages = reader.iter_decoded_messages(
                    topics,
                    start_seconds * 1e9 if start_seconds else None,
                    end_seconds * 1e9 if end_seconds else None,
                )

                for _, channel, message, decoded_message in messages:
                    record = {
                        settings.ROBOLOG_ID_COLUMN_NAME: self.robolog_id,
                        settings.TIMESTAMP_SECONDS_COLUMN_NAME: message.log_time / 1e9,
                        settings.TOPIC_COLUMN_NAME: channel.topic,
                        settings.MESSAGE_COLUMN_NAME: converter.to_dict(decoded_message),
                    }

                    for column, value in record.items():
                        batch[column].append(value)

                    if len(batch[settings.ROBOLOG_ID_COLUMN_NAME]) >= batch_size:
                        record_batch = pa.RecordBatch.from_pydict(batch, schema=schema)
                        batch_size = self._estimate_record_batch_size_count(record_batch)
                        batch = {column: [] for column in schema.names}
                        yield record_batch

        if batch[settings.ROBOLOG_ID_COLUMN_NAME]:
            yield pa.RecordBatch.from_pydict(batch, schema=schema)
