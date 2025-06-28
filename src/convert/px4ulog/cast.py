"""Convert PX4 ULog message schema to PyArrow DataTypes."""

import pyarrow as pa
import yaml


def cast(type_str: str) -> pa.DataType:  # noqa: C901, PLR0912
    """Cast a PX4 ULog type string to a PyArrow DataType."""
    match type_str:
        case "int8_t":
            pa_type = pa.int8()
        case "uint8_t":
            pa_type = pa.uint8()
        case "int16_t":
            pa_type = pa.int16()
        case "uint16_t":
            pa_type = pa.uint16()
        case "int32_t":
            pa_type = pa.int32()
        case "uint32_t":
            pa_type = pa.uint32()
        case "int64_t":
            pa_type = pa.int64()
        case "uint64_t":
            pa_type = pa.uint64()
        case "float":
            pa_type = pa.float32()
        case "double":
            pa_type = pa.float64()
        case "bool":
            pa_type = pa.int8()
        case "char":
            pa_type = pa.int8()
        case _:
            raise ValueError(f"Unsupported type: {type_str}")
    return pa_type


def to_pa_struct(yaml_string: str) -> pa.StructType:
    """Convert a YAML string representing a PX4 ULog message schema to a PyArrow StructType.

    Args:
        yaml_string (str): A YAML string representing the message schema.

    Returns:
        pa.StructType: The corresponding PyArrow StructType.

    """
    schema = yaml.safe_load(yaml_string)
    fields = []
    for field_name, type_str in schema.items():
        fields.append(pa.field(field_name, cast(type_str), nullable=False))
    return pa.struct(fields)
