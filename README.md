# 🥯 Bag Extraction Tool
`bagel` extracts and transforms topic messages from robotics logs into DataFrames, fast.

It supports multiple log formats.

| Format                        | Encodings                  |
| ----------------------------- | -------------------------- |
| :white_check_mark: ROS2 .mcap | ros1msg, ros2msg, protobuf |
| :white_check_mark: ROS2 .db3  | ros2msg                    |
| :white_check_mark: ROS1 .bag  | ros1msg                    |
| :white_check_mark: PX4 .ulg   | ULog                       |
