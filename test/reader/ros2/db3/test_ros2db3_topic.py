import pathlib

from settings import settings
from src.reader.ros2.db3.topic import TopicMessageReader


def test_has_correct_properties() -> None:
    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag"

    # WHEN
    reader = TopicMessageReader(robolog_path)

    # THEN
    assert reader.robolog_id == "05c3e102-656e-5ed9-b881-0cdd925635c4"
    assert reader.start_seconds == 2.623e-06
    assert reader.end_seconds == 3.034e-06
    assert reader.duration_seconds == 4.1099999999999996e-07
    assert reader.path == robolog_path.absolute()
    assert reader.size_bytes == 439962
    assert reader.message_count == 6074
    assert sorted(reader.topics) == ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]
    assert reader.type_names == {
        "AAA": "std_msgs/msg/String",
        "BBB": "std_msgs/msg/String",
        "CCC": "std_msgs/msg/String",
        "DDD": "std_msgs/msg/String",
        "EEE": "std_msgs/msg/String",
        "FFF": "std_msgs/msg/String",
        "GGG": "std_msgs/msg/String",
        "HHH": "std_msgs/msg/String",
    }

    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag" / "wbag_0.db3"

    # WHEN
    reader = TopicMessageReader(robolog_path)

    # THEN
    assert reader.robolog_id == "7517454e-9005-5e6c-b87d-8c1dc8415a32"
    assert reader.start_seconds == 1e-06
    assert reader.end_seconds == 1.408e-06
    assert reader.duration_seconds == 4.0799999999999995e-07
    assert reader.path == robolog_path.absolute()
    assert reader.size_bytes == 90112
    assert reader.message_count == 1246
    assert sorted(reader.topics) == ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]
    assert reader.type_names == {
        "AAA": "std_msgs/msg/String",
        "BBB": "std_msgs/msg/String",
        "CCC": "std_msgs/msg/String",
        "DDD": "std_msgs/msg/String",
        "EEE": "std_msgs/msg/String",
        "FFF": "std_msgs/msg/String",
        "GGG": "std_msgs/msg/String",
        "HHH": "std_msgs/msg/String",
    }


def test_can_all_read_messages() -> None:
    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag"
    reader = TopicMessageReader(robolog_path)

    # WHEN
    table = reader.read().to_table()

    # THEN
    assert table.num_rows == 6074
    assert set(table.column_names) == set(
        [
            settings.ROBOLOG_ID_COLUMN_NAME,
            settings.TIMESTAMP_SECONDS_COLUMN_NAME,
            "AAA",
            "BBB",
            "CCC",
            "DDD",
            "EEE",
            "FFF",
            "GGG",
            "HHH",
        ]
    )


def test_can_read_topics() -> None:
    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag"
    reader = TopicMessageReader(robolog_path)

    # WHEN
    table = reader.read(["AAA"]).to_table()

    # THEN
    assert table.num_rows == 804
    assert table.column_names == [
        settings.ROBOLOG_ID_COLUMN_NAME,
        settings.TIMESTAMP_SECONDS_COLUMN_NAME,
        "AAA",
    ]


def test_can_read_time_range() -> None:
    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag"
    reader = TopicMessageReader(robolog_path)

    # WHEN
    table = reader.read(start_seconds=2000 / 1e9).to_table()

    # THEN
    assert table.num_rows == 3064

    # WHEN
    table = reader.read(start_seconds=2000 / 1e9, end_seconds=2500 / 1e9).to_table()

    # THEN
    assert table.num_rows == 1582

    # WHEN
    table = reader.read(end_seconds=2000 / 1e9).to_table()

    # THEN
    assert table.num_rows == 3016


def test_can_apply_asof_join() -> None:
    # GIVEN
    robolog_path = pathlib.Path(__file__).parent / "data" / "wbag"
    reader = TopicMessageReader(robolog_path)

    # WHEN
    table = reader.read(asof_join=True).to_table()

    # THEN
    assert table.to_pandas()["EEE"].notnull().all()
