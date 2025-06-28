import textwrap

from src.convert.ros2msg import definition, parse


def test_should_parse_sample_full_text() -> None:
    # GIVEN
    full_text = """
    # This message contains an uncompressed image
    # (0, 0) is at top-left corner of image

    std_msgs/Header header # Header timestamp should be acquisition time of image
                                # Header frame_id should be optical frame of camera
                                # origin of frame should be optical center of cameara
                                # +x should point to the right in the image
                                # +y should point down in the image
                                # +z should point into to plane of the image
                                # If the frame_id here and the frame_id of the CameraInfo
                                # message associated with the image conflict
                                # the behavior is undefined

    uint32 height                # image height, that is, number of rows
    uint32 width                 # image width, that is, number of columns

    # The legal values for encoding are in file include/sensor_msgs/image_encodings.hpp
    # If you want to standardize a new string format, join
    # ros-users@lists.ros.org and send an email proposing a new encoding.

    string encoding       # Encoding of pixels -- channel meaning, ordering, size
                        # taken from the list of strings in include/sensor_msgs/image_encodings.hpp

    uint8 is_bigendian    # is this data bigendian?
    uint32 step           # Full row length in bytes
    uint8[] data          # actual matrix data, size is (step * rows)

    ================================================================================
    MSG: std_msgs/Header
    # Standard metadata for higher-level stamped data types.
    # This is generally used to communicate timestamped data
    # in a particular coordinate frame.

    # Two-integer timestamp that is expressed as seconds and nanoseconds.
    builtin_interfaces/Time stamp

    # Transform frame with which this data is associated.
    string frame_id

    ================================================================================
    MSG: builtin_interfaces/Time
    # This message communicates ROS Time defined here:
    # https://design.ros2.org/articles/clock_and_time.html

    # The seconds component, valid over all int32 values.
    int32 sec

    # The nanoseconds component, valid in the range [0, 1e9).
    uint32 nanosec
    """

    # WHEN
    struct, deps = parse.parse(textwrap.dedent(full_text))

    # THEN
    assert struct.fields == [
        definition.ComplexField(
            name="header",
            type_="std_msgs/Header",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
        ),
        definition.UintField(
            name="height",
            type_="uint32",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            default=None,
        ),
        definition.UintField(
            name="width",
            type_="uint32",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            default=None,
        ),
        definition.StringField(
            name="encoding",
            type_="string",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            string_size_upper_bound=None,
            default="",
        ),
        definition.UintField(
            name="is_bigendian",
            type_="uint8",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            default=None,
        ),
        definition.UintField(
            name="step",
            type_="uint32",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            default=None,
        ),
        definition.UintField(
            name="data",
            type_="uint8",
            is_array=True,
            array_size=None,
            array_size_upper_bound=None,
            default=None,
        ),
    ]
    assert deps["std_msgs/Header"].fields == [
        definition.ComplexField(
            name="stamp",
            type_="builtin_interfaces/Time",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
        ),
        definition.StringField(
            name="frame_id",
            type_="string",
            is_array=False,
            array_size=None,
            array_size_upper_bound=None,
            string_size_upper_bound=None,
            default=None,
        ),
    ]
