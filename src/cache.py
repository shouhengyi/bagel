"""Artifact cache management with deterministic file naming."""

import pathlib
import shutil

from settings import settings


def _clear_directory(directory: pathlib.Path) -> int:
    """Clear a directory and return the total bytes cleared."""
    if not directory.exists() or not directory.is_dir():
        return 0
    bytes_cleared = sum(f.stat().st_size for f in directory.glob("**/*") if f.is_file())
    shutil.rmtree(directory)
    return bytes_cleared


def clear_all_cache() -> int:
    """Clear the entire cache directory and return the total bytes cleared."""
    return _clear_directory(pathlib.Path(settings.CACHE_DIRECTORY))


def clear_all_storage() -> int:
    """Clear the entire storage directory and return the total bytes cleared."""
    return _clear_directory(pathlib.Path(settings.STORAGE_DIRECTORY))
