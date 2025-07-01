"""Utility functions for the web application."""

import time
from collections.abc import Iterator


def stream(text: str, seconds: int = 0.02) -> Iterator[str]:
    """Yield each character in the text with a delay."""
    for char in text:
        yield char
        time.sleep(seconds)
