import textwrap

import lark
import pytest

from src.convert.ros1msg import definition, parse


def test_should_parse_empty_definition() -> None:
    # GIVEN
    full_text = ""

    # WHEN
    struct, deps = parse.parse(full_text)

    # THEN
    assert struct.fields == []
    assert deps == {}


def test_should_ignore_empty_and_comment_lines() -> None:
    # GIVEN
    full_text = """
    # This is a comment line
    some/msg/CustomType field0  # This is an inline comment
    some/msg/CustomType[] field_1        # Another inline comment
    some/msg/CustomType[10] Field__2

    # Yet another comment line
    ========================

    # Comment before the message definition
    # ========================
    MSG: some/msg/CustomType  # Comment after MSG definition
    int32 a
    string b
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="field0", type_="some/msg/CustomType", is_array=False, array_size=None
        ),
        definition.ComplexField(
            name="field_1", type_="some/msg/CustomType", is_array=True, array_size=None
        ),
        definition.ComplexField(
            name="Field__2", type_="some/msg/CustomType", is_array=True, array_size=10
        ),
    ]

    assert deps == {
        "some/msg/CustomType": definition.Struct(
            type_="some/msg/CustomType",
            fields=[
                definition.BuiltInField(name="a", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="b", type_="string", is_array=False, array_size=None),
            ],
        )
    }


def test_should_parse_valid_complex_type_and_names() -> None:
    # GIVEN
    full_text = """
    some/msg/CustomType field0
    some/msg/CustomType[] field_1
    some/msg/CustomType[10] Field__2

    ========================
    MSG: some/msg/CustomType
    int32 a
    string b
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="field0", type_="some/msg/CustomType", is_array=False, array_size=None
        ),
        definition.ComplexField(
            name="field_1", type_="some/msg/CustomType", is_array=True, array_size=None
        ),
        definition.ComplexField(
            name="Field__2", type_="some/msg/CustomType", is_array=True, array_size=10
        ),
    ]

    assert deps == {
        "some/msg/CustomType": definition.Struct(
            type_="some/msg/CustomType",
            fields=[
                definition.BuiltInField(name="a", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="b", type_="string", is_array=False, array_size=None),
            ],
        )
    }


def test_should_raise_if_complex_type_is_invalid() -> None:
    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some_custom_type name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/custom_type name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("_some/CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some_/CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/_CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/CustomType_ name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("0some/CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("/some/CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("/CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some//CustomType name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/Custom/Type name")


def test_should_raise_if_name_is_invalid() -> None:
    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/CustomType _name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/CustomType 0name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("some/CustomType some/name")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("int32 _name=123")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("int32 0name=123")

    with pytest.raises(lark.exceptions.UnexpectedCharacters):
        parse.parse("int32 some/name=123")


def test_should_raise_if_fixed_length_array_field_has_non_positive_size() -> None:
    # GIVEN
    full_text = "some/CustomType[0] name"

    # WHEN / THEN
    with pytest.raises(
        parse.InvalidArrayTokenError,
        match="Array size must be a positive integer, got 0",
    ):
        parse.parse(full_text)


def test_should_resolve_unqualified_complex_type() -> None:
    # GIVEN
    full_text = """
    CustomType field0

    ========================
    MSG: some/msg/CustomType
    int32 a
    string b
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="field0", type_="some/msg/CustomType", is_array=False, array_size=None
        ),
    ]

    assert deps == {
        "some/msg/CustomType": definition.Struct(
            type_="some/msg/CustomType",
            fields=[
                definition.BuiltInField(name="a", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="b", type_="string", is_array=False, array_size=None),
            ],
        )
    }


def test_should_ignore_whitespaces() -> None:
    # GIVEN
    full_text = """
    int32  name
    int32\tname
    int32  \tname
    int32 name\t
    int32 name 
    int32 name = 123
    int32 name =123
    int32 name= 123
    int32 name=123 
    int32 name\t=\t123
    int32 name\t=123
    int32 name=\t123
    int32 name=123\t
    """  # noqa: W291

    # WHEN
    struct, _ = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert (
        struct.fields
        == [definition.BuiltInField(name="name", type_="int32", is_array=False, array_size=None)]
        * 5
        + [definition.Constant(name="name", type_="int32", value=123)] * 8
    )


def test_should_not_mix_up_same_class_name_from_different_packages() -> None:
    # GIVEN
    full_text = """
    some/msg/CustomType field0

    ========================
    MSG: some/msg/CustomType
    int32 a
    string b

    ========================
    MSG: other/msg/CustomType
    int32 c
    string d
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="field0", type_="some/msg/CustomType", is_array=False, array_size=None
        )
    ]

    assert deps == {
        "some/msg/CustomType": definition.Struct(
            type_="some/msg/CustomType",
            fields=[
                definition.BuiltInField(name="a", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="b", type_="string", is_array=False, array_size=None),
            ],
        ),
        "other/msg/CustomType": definition.Struct(
            type_="other/msg/CustomType",
            fields=[
                definition.BuiltInField(name="c", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="d", type_="string", is_array=False, array_size=None),
            ],
        ),
    }


def test_should_resolve_header_type_correctly() -> None:
    # GIVEN
    full_text = """
    Header header

    ========================
    MSG: std_msgs/Header
    uint32 seq
    time stamp
    string frame_id
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="header", type_="std_msgs/Header", is_array=False, array_size=None
        )
    ]

    assert deps == {
        "std_msgs/Header": definition.Struct(
            type_="std_msgs/Header",
            fields=[
                definition.BuiltInField(
                    name="seq", type_="uint32", is_array=False, array_size=None
                ),
                definition.BuiltInField(
                    name="stamp", type_="time", is_array=False, array_size=None
                ),
                definition.BuiltInField(
                    name="frame_id", type_="string", is_array=False, array_size=None
                ),
            ],
        )
    }


def test_should_parse_if_duplicated_type_definition() -> None:
    # GIVEN
    full_text = """
    some/msg/CustomType field0

    ========================
    MSG: some/msg/CustomType
    int32 a
    string b

    ========================
    MSG: some/msg/CustomType
    int32 a
    string b
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="field0", type_="some/msg/CustomType", is_array=False, array_size=None
        )
    ]

    assert deps == {
        "some/msg/CustomType": definition.Struct(
            type_="some/msg/CustomType",
            fields=[
                definition.BuiltInField(name="a", type_="int32", is_array=False, array_size=None),
                definition.BuiltInField(name="b", type_="string", is_array=False, array_size=None),
            ],
        )
    }
