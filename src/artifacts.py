"""Artifacts created by the application."""

import hashlib
import pathlib

from settings import settings
from src import robolog


def _short_digest(seeds: list[str]) -> str:
    """Generate a short SHA-256 digest from a list of seeds."""
    return hashlib.sha256("_".join(seeds).encode("utf8")).hexdigest()[:8]


def _snippet_path(
    robolog_path: str | pathlib.Path, start_seconds: float, end_seconds: float
) -> pathlib.Path:
    """Generate a cache path for a snippet of the robolog."""
    return pathlib.Path(settings.CACHE_DIRECTORY) / robolog.snippet_name(
        robolog_path, start_seconds, end_seconds
    )


def topic_arrow_file(  # noqa: PLR0913
    robolog_path: str | pathlib.Path,
    topics: list[str],
    start_seconds: float,
    end_seconds: float,
    ffill: bool,
    peek: bool,
) -> pathlib.Path:
    """Generate an Arrow file path containing message time series of selected topics."""
    seeds = [str(sorted(topics)), str(ffill)]
    digest = _short_digest(seeds)
    file_name = f"topic_{digest}.arrow" if not peek else f"topic_{digest}_peek.arrow"
    return _snippet_path(robolog_path, start_seconds, end_seconds) / file_name


def type_arrow_file(
    robolog_path: str | pathlib.Path,
    type_name: str,
    start_seconds: float,
    end_seconds: float,
) -> pathlib.Path:
    """Generate an Arrow file path containing message time series of a specific message type."""
    seeds = [type_name]
    return (
        _snippet_path(robolog_path, start_seconds, end_seconds)
        / f"type_{_short_digest(seeds)}.arrow"
    )


def frequency_arrow_file(
    robolog_path: str | pathlib.Path,
    topics: list[str],
    start_seconds: float,
    end_seconds: float,
) -> pathlib.Path:
    """Generate an Arrow file path containing message frequency time series of selected topics."""
    seeds = [str(sorted(topics))]
    return (
        _snippet_path(robolog_path, start_seconds, end_seconds)
        / f"frequency_{_short_digest(seeds)}.arrow"
    )
