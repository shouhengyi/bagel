"""Return metadata from a PX4 .ulog file as a JSON-serializable dictionary."""

import functools
import pathlib
from typing import Any

from pyulog import core

from src.reader.metadata import find_primitives


def to_dict(ulog: core.ULog) -> dict[str, Any]:
    """Return metadata from a core.ULog object as a JSON-serializable dictionary.

    ULog must be initialized with `parse_header_only=False` to include all topics.

    """
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


@functools.lru_cache(maxsize=128)
def extract_metadata(robolog_path: str | pathlib.Path) -> dict[str, Any]:
    """Return metadata from a PX4 .ulog file as a JSON-serializable dictionary.

    Args:
        robolog_path (str | pathlib.Path): Path to the PX4 .ulog file.

    Returns:
        dict[str, Any]: Robolog's metadata as a JSON-serializable dictionary.

    """
    return to_dict(core.ULog(str(robolog_path), parse_header_only=False))
