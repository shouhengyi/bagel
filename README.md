<p align="center">
  <img src="./doc/assets/logo.svg">
</p>

---

# Bagel: Bag Extraction Tool

Bagel allows you to extract, transform, and analyze robotics data — fast.

How fast? Cast topic messages to a **pandas `DataFrame`** or **PyArrow `Dataset`** in under four lines of code.

```py
from src.reader import factory

reader = factory.make_topic_message_reader("./doc/tutorials/data/ros2")
ds = reader.read(["/fluid_pressure"])  # return a pyarrow Dataset
df = ds.to_table().to_pandas()         # cast into a pandas DataFrame
```

You can do much more! Whether you're performing granular robot-level troubleshooting, analyzing fleet-wide performance metrics, or creating high-level executive dashboards, Bagel gets the job done.

[Get started today](#getting-started)

[Join our Discord server](https://discord.gg/KVKEmq3A)

### A Sneak Peek

Bagel can visualize camera latency from a robolog:

<p align="center">
  <img src="./doc/assets/latency.png">
</p>

...or aggregate fleet-level exceptions over time:

<p align="center">
  <img src="./doc/assets/fleet_exceptions.png">
</p>

### Log Formats

Bagel is designed to ingest a wide range of common robotics and sensor log formats out of the box.

| Format                         | Supported Encodings        |
| ------------------------------ | -------------------------- |
| ✅ **ROS 2** (`.mcap`, `.db3`) | `ros1`, `ros2`, `protobuf` |
| ✅ **ROS 1** (`.bag`)          | `ros1`                     |
| ✅ **PX4** (`.ulg`)            | `ULog`                     |

#### Don’t See Your Format?

Bagel is built to be extensible. If your preferred format isn’t listed, we encourage you to **[open a feature request](https://github.com/shouhengyi/bagel/issues)** to start a discussion!

## Getting Started

### Tutorials

- [Calculating Acceleration Statistics from a PX4 ULog](./doc/tutorials/pipelines/0_basics.ipynb)
- [Reading Topic Messages from a ROS 2 Bag](./doc/tutorials/readers/1_read_by_topic.ipynb)

### Running in Docker 🐳

To run Bagel without installing local dependencies like ROS, you can use our provided Docker images. Make sure you have [Docker Desktop](https://docs.docker.com/desktop/) installed. This example uses ROS 2 Kilted.

#### Mount Your Data

First, give the container access to your robolog files. Open the [compose.yaml](./compose.yaml) file and find the service you want to use (e.g., ros2-kilted). Edit the volumes section to link your local data folder to the container's data folder.

```yaml
services:
  ros2-kilted:
    ...
    # volumes:                                     <-- ✅ Uncomment
    #   - <path-to-local-data>:/home/ubuntu/data   <-- ✅ Uncomment & Replace
```

#### Launch the App

Build and start the container with a single command.

```sh
docker compose up --build ros2-kilted
```

For future runs, you can omit the --build flag.

Your local robolog files are now accessible inside the container at `/home/ubuntu/data`.

### Running Locally 🛠️

If local dependencies like ROS are already installed, you can run Bagel directly on your machine.

#### Prerequisites

First, ensure you have the following tools installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/)

#### Install & Run

Next, use Poetry to install the project dependencies and run the application.

```sh
poetry install
poetry run python3 main.py up
```
