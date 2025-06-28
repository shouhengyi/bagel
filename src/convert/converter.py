"""Base class for converting messages into JSON-serializable dictionaries."""

import abc
from typing import Any


class MessageConverter(abc.ABC):
    """Abstract base class for converting messages into dictionaries."""

    @abc.abstractmethod
    def to_dict(self, message: object) -> dict[str, Any]:
        """Convert a message to a JSON-serializable dictionary."""
