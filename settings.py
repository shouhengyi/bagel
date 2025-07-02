"""Settings for the bagel application."""

import logging
import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB


class Settings(BaseSettings):
    """Settings for the bagel application."""

    model_config = SettingsConfigDict(
        env_prefix="BAGEL_",
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Logging level for the application
    LOG_LEVEL: int = logging.INFO

    # Whether to use cached data when available
    USE_CACHE: bool = True

    # Directory for caching intermediate artifacts
    CACHE_DIRECTORY: str = str(pathlib.Path.home() / ".cache" / "bagel")

    # Directory for persisting final artifacts
    STORAGE_DIRECTORY: str = str(pathlib.Path.home() / ".bagel")

    # Minimum number of records per batch in arrow files
    MIN_ARROW_RECORD_BATCH_SIZE_COUNT: int = 500

    # Bytes per record batch in arrow files. Not always respected
    ARROW_RECORD_BATCH_SIZE_BYTES: int = 1 * GB

    # Column name for robolog UUID in arrow files
    ROBOLOG_ID_COLUMN_NAME: str = "robolog_id"

    # Column name for timestamps in arrow files, i.e., when messages were recorded
    TIMESTAMP_SECONDS_COLUMN_NAME: str = "timestamp_seconds"

    # Column name for the topic in arrow files
    TOPIC_COLUMN_NAME: str = "topic"

    # Column name for the message in arrow files
    MESSAGE_COLUMN_NAME: str = "message"

    # Maximum number of rows to display in DuckDB queries
    DUCKDB_DISPLAY_MAX_ROWS: int = 3

    # Port of the local webapp
    WEBAPP_LOCAL_PORT: int = 8501

    # Streamlit webapp path
    WEBAPP_PATH: str = "app.py"


settings = Settings()

pathlib.Path(settings.CACHE_DIRECTORY).mkdir(parents=True, exist_ok=True)
