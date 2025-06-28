"""Base class for calculating message frequencies."""

import logging
from collections.abc import Iterator

import humanize
import pyarrow as pa
import pyarrow.dataset as ds

from settings import settings
from src import artifacts
from src.reader.reader import Reader

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


class TopicFrequencyReader(Reader):
    """Base class for calculating message frequencies."""

    def read(
        self,
        topics: list[str] | None = None,
        start_seconds: float | None = None,
        end_seconds: float | None = None,
    ) -> ds.Dataset:
        """Return message frequencies for the specified topics and time range.

        Args:
            topics (list[str] | None, optional): Topics to read from. If None, all topics are read.
            start_seconds (float | None, optional): When to start reading messages.
            end_seconds (float | None, optional): When to stop reading messages.

        Returns:
            ds.Dataset: A PyArrow dataset containing the message frequencies.

        """
        topics = topics or self.topics
        self._raise_if_missing_topics(topics)
        if not topics:
            raise ValueError("No topics specified for reading messages.")

        logger.debug(
            "Reading topics %s from %s to %s",
            topics,
            start_seconds or self.start_seconds,
            end_seconds or self.end_seconds,
        )

        arrow_file = artifacts.frequency_arrow_file(
            self.path,
            topics,
            start_seconds or self.start_seconds,
            end_seconds or self.end_seconds,
        )
        if arrow_file.exists() and self._use_cache:
            logger.debug("Return from cache %s", arrow_file)
            return ds.dataset(arrow_file, format="arrow")
        arrow_file.unlink(missing_ok=True)
        arrow_file.parent.mkdir(parents=True, exist_ok=True)

        schema = pa.schema(
            [
                pa.field(settings.ROBOLOG_ID_COLUMN_NAME, pa.string(), nullable=False),
                pa.field(settings.TIMESTAMP_SECONDS_COLUMN_NAME, pa.float64(), nullable=False),
            ]
        )
        for topic in topics:
            schema = schema.append(pa.field(topic, pa.float64(), nullable=True))

        try:
            with (
                pa.OSFile(str(arrow_file), "wb") as sink,
                pa.RecordBatchFileWriter(sink, schema=schema) as writer,
            ):
                for record_batch in self._iter_record_batches(
                    topics, start_seconds, end_seconds, schema
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
    ) -> Iterator[pa.RecordBatch]:
        """Iterate over record batches for the specified topics and time range."""
        raise NotImplementedError()
