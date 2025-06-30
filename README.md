# 🥯 Bag Extraction Tool
`bagel` extracts and transforms topic messages from robotics logs into DataFrames, fast.

How fast? With just 20 lines of YAML, you can extract all camera intrinsics from a ROS bag.

Here is an example that extracts camera intrinsic parameters:

```yaml
# camera_intrinsics.yaml

extract_type:
  - name: camera_info
    type_name: sensor_msgs/CameraInfo

transform_dataframe:
  - name: camera_intrinsics
    sql: |
      SELECT DISTINCT
          message.width,
          message.height,
          message.header.frame_id as camera_name,
          {'rows': 3, 'cols': 3, 'data': message.K} camera_matrix,
          message.distortion_model,
          {'rows': 1, 'cols': 5, 'data': message.D} as distortion_coefficients,
          {'rows': 3, 'cols': 3, 'data': message.R} as rectification_matrix,
          {'rows': 3, 'cols': 4, 'data': message.P} as projection_matrix
      FROM camera_info

save_dataframe:
  - camera_intrinsics
```

It supports multiple log formats.

| Format                        | Encodings                  |
| ----------------------------- | -------------------------- |
| :white_check_mark: ROS2 .mcap | ros1msg, ros2msg, protobuf |
| :white_check_mark: ROS2 .db3  | ros2msg                    |
| :white_check_mark: ROS1 .bag  | ros1msg                    |
| :white_check_mark: PX4 .ulg   | ULog                       |
