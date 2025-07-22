"""Helper functions to parse metadata from a robolog."""

from typing import Any

PY_PRIMITIVE_TYPES = (bool, int, float, str, type(None))  # bytes type is not JSON serializable


def is_primitive(value: object) -> bool:
    """Determine if a value is a primitive type or a list of primitive types."""
    if isinstance(value, PY_PRIMITIVE_TYPES):
        return True
    elif isinstance(value, list):
        return all(isinstance(item, PY_PRIMITIVE_TYPES) for item in value)
    return False


def find_primitives(data: object) -> dict[str, Any]:
    """Find all public properties of an object that are primitive types."""
    return {
        prop: getattr(data, prop)
        for prop in dir(data)
        if (
            not prop.startswith("_")  # ignore private attributes
            and not prop.startswith("__")  # ignore dunder methods, class methods, etc.
            and is_primitive(getattr(data, prop))
        )
    }
