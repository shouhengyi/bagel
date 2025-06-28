"""Base class for reading messages of a specific message type."""

import logging
from collections.abc import Iterator

import humanize
import pyarrow as pa
import pyarrow.dataset as ds

from settings import settings
from src import artifacts
from src.convert import factory
from src.convert.converter import MessageConverter
from src.reader.reader import Reader

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


class TypeMessageReader(Reader):
    """Base class for reading messages of a specific message type."""

    def read(
        self,
        type_name: str,
        start_seconds: float | None = None,
        end_seconds: float | None = None,
        converter: MessageConverter | None = None,
        exclude_topics: list[str] | None = None,
    ) -> ds.Dataset:
        """Return messages of a specific message type and time range.

        Args:
            type_name (str): The message type to read messages for.
            start_seconds (float | None, optional): When to start reading messages.
            end_seconds (float | None, optional): When to stop reading messages.
            converter (MessageConverter | None, optional): A converter for the message type.
                If provided, it will take precedence over the default converter for the type.
            exclude_topics (list[str] | None, optional): A list of topics to exclude from the
                dataset. If None, no topics will be excluded.

        Returns:
            ds.Dataset: A PyArrow dataset containing messages of the specified type.

        """
        self._raise_if_missing_type(type_name)

        topics = [
            topic
            for topic, type_name_ in self.type_names.items()
            if type_name_ == type_name and topic not in (exclude_topics or [])
        ]
        if not topics:
            raise ValueError(f"No topics found for type: {type_name}")

        logger.debug(
            "Reading topics %s from %s to %s",
            topics,
            start_seconds or self.start_seconds,
            end_seconds or self.end_seconds,
        )

        arrow_file = artifacts.type_arrow_file(
            self.path,
            type_name,
            start_seconds or self.start_seconds,
            end_seconds or self.end_seconds,
        )
        if arrow_file.exists() and self._use_cache:
            logger.debug("Return from cache %s", arrow_file)
            return ds.dataset(arrow_file, format="arrow")
        arrow_file.unlink(missing_ok=True)
        arrow_file.parent.mkdir(parents=True, exist_ok=True)

        converter = converter or factory.make_converter(self.path, type_name)

        schema = pa.schema(
            [
                pa.field(settings.ROBOLOG_ID_COLUMN_NAME, pa.string(), nullable=False),
                pa.field(settings.TIMESTAMP_SECONDS_COLUMN_NAME, pa.float64(), nullable=False),
                pa.field(settings.TOPIC_COLUMN_NAME, pa.string(), nullable=False),
                pa.field(settings.MESSAGE_COLUMN_NAME, converter.pa_struct, nullable=False),
            ]
        )

        try:
            with (
                pa.OSFile(str(arrow_file), "wb") as sink,
                pa.RecordBatchFileWriter(sink, schema=schema) as writer,
            ):
                for record_batch in self._iter_record_batches(
                    topics, start_seconds, end_seconds, schema, converter
                ):
                    writer.write_batch(record_batch)
                    logger.debug(
                        "Appended record batch of size %d with %d rows",
                        humanize.naturalsize(record_batch.nbytes),
                        humanize.intcomma(record_batch.num_rows),
                    )

            logger.debug("Created dataset and cached to %s", arrow_file)
            return ds.dataset(arrow_file, format="arrow")

        except Exception as e:
            arrow_file.unlink(missing_ok=True)
            raise e

    def _iter_record_batches(
        self,
        topics: list[str],
        start_seconds: float | None,
        end_seconds: float | None,
        schema: pa.Schema,
        converter: MessageConverter,
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        raise NotImplementedError()
