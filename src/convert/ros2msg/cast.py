"""Convert ROS2 message definitions to PyArrow DataTypes."""

import pyarrow as pa

from src.convert.ros2msg import definition


def cast_constant(constant: definition.Constant) -> pa.DataType:  # noqa: C901, PLR0912
    """Cast a ROS2 Constant to its corresponding PyArrow DataType."""
    match constant:
        case definition.Constant(type_="bool"):
            pa_type = pa.bool_()
        case definition.Constant(type_="uint8"):
            pa_type = pa.uint8()
        case definition.Constant(type_="uint16"):
            pa_type = pa.uint16()
        case definition.Constant(type_="uint32"):
            pa_type = pa.uint32()
        case definition.Constant(type_="uint64"):
            pa_type = pa.uint64()
        case definition.Constant(type_="int8"):
            pa_type = pa.int8()
        case definition.Constant(type_="int16"):
            pa_type = pa.int16()
        case definition.Constant(type_="int32"):
            pa_type = pa.int32()
        case definition.Constant(type_="int64"):
            pa_type = pa.int64()
        case definition.Constant(type_="float32"):
            pa_type = pa.float32()
        case definition.Constant(type_="float64"):
            pa_type = pa.float64()
        case definition.Constant(type_="char"):
            pa_type = pa.uint8()
        case definition.Constant(type_="byte"):
            pa_type = pa.int8()
        case definition.Constant(type_="string") | definition.Constant(type_="wstring"):
            pa_type = pa.string()
        case _:
            raise ValueError(f"Unsupported constant type: {constant.type_}")

    return pa_type


def cast_builtin_field(field: definition.BuiltInField) -> pa.DataType:  # noqa: C901, PLR0912
    """Cast a ROS2 BuiltInField to its corresponding PyArrow DataType."""
    match field:
        case definition.BoolField(type_="bool"):
            pa_type = pa.bool_()
        case definition.UintField(type_="uint8"):
            pa_type = pa.uint8()
        case definition.UintField(type_="uint16"):
            pa_type = pa.uint16()
        case definition.UintField(type_="uint32"):
            pa_type = pa.uint32()
        case definition.UintField(type_="uint64"):
            pa_type = pa.uint64()
        case definition.IntField(type_="int8"):
            pa_type = pa.int8()
        case definition.IntField(type_="int16"):
            pa_type = pa.int16()
        case definition.IntField(type_="int32"):
            pa_type = pa.int32()
        case definition.IntField(type_="int64"):
            pa_type = pa.int64()
        case definition.FloatField(type_="float32"):
            pa_type = pa.float32()
        case definition.FloatField(type_="float64"):
            pa_type = pa.float64()
        case definition.CharField(type_="char"):
            pa_type = pa.uint8()
        case definition.ByteField(type_="byte"):
            pa_type = pa.int8()
        case definition.StringField(type_="string") | definition.StringField(type_="wstring"):
            pa_type = pa.string()
        case _:
            raise ValueError(f"Unsupported built-in field type: {field.type_}")

    if not field.is_array:
        return pa_type
    else:
        return pa.list_(
            pa_type,
            field.array_size if field.array_size is not None else -1,
        )


##########################################################################
### Significant duplications of code with ros1msg/cast.py from here on ###
### This is tolerable as we might split code for into packages         ###
##########################################################################


def cast_field(field: definition.Field, dependencies: dict[str, definition.Struct]) -> pa.Field:
    """Cast a ROS2 Field to its corresponding PyArrow Field."""
    match field:
        case definition.Constant():
            return pa.field(field.name, cast_constant(field), nullable=False)

        case definition.BuiltInField():
            return pa.field(field.name, cast_builtin_field(field), nullable=False)

        case definition.ComplexField():
            children = []
            for sub_field in dependencies[field.type_].fields:
                children.append(cast_field(sub_field, dependencies))
            pa_struct = pa.struct(children)

            if field.is_array:
                pa_type = pa.list_(
                    pa_struct,
                    field.array_size if field.array_size is not None else -1,
                )
            else:
                pa_type = pa_struct

            return pa.field(field.name, pa_type, nullable=False)

        case _:
            raise ValueError(f"Unsupported field type: {field.type_}")


def to_pa_struct(
    main: definition.Struct, dependencies: dict[str, definition.Struct]
) -> pa.StructType:
    """Convert a ROS2 message definition text to a PyArrow StructType.

    Args:
        main (definition.Struct): The main message definition.
        dependencies (dict[str, definition.Struct]): Dependency definitions of the main definition.

    Returns:
        pa.StructType: The corresponding PyArrow StructType.

    """
    children = []
    for field in main.fields:
        children.append(cast_field(field, dependencies))
    return pa.struct(children)
