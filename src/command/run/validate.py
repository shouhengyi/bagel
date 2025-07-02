"""Utility functions to validate input strings."""

import re
from collections import Counter


class DataFrameAlreadyDefinedError(Exception):
    """Raised when a DataFrame with the same name is already defined."""


def validate_snake_case(s: str) -> None:
    """Raise if a string is not in snake_case format."""
    if not isinstance(s, str) or not s or s.startswith("_") or s.endswith("_") or "__" in s:
        is_snake_case = False
    else:
        all_lowercase_alphanumeric_chars_and_underscores = (
            re.fullmatch(r"[a-z0-9_]+", s) is not None
        )
        no_uppercase_chars = re.search(r"[A-Z]", s) is None
        is_snake_case = all_lowercase_alphanumeric_chars_and_underscores and no_uppercase_chars

    if not is_snake_case:
        raise ValueError(f"'{s}' is not in snake_case format.")


def validate_unique_dataframe_names(names: list[str]) -> None:
    """Raise if there are duplicate DataFrame names."""
    name_counts = Counter(names)
    duplicates = [name for name, count in name_counts.items() if count > 1]

    if duplicates:
        raise DataFrameAlreadyDefinedError(", ".join(duplicates))
