<p align="center">
  <img src="./doc/assets/logo.svg">
</p>

---

# Bagel: Bag Extraction Tool

Bagel allows you to extract, transform, and analyze robotics data — fast.

Whether you're performing granular robot-level troubleshooting, analyzing fleet-wide performance metrics, or creating high-level executive dashboards, Bagel gets the job done.

[Get started today](#getting-started) — no account needed.

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

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Poetry](https://python-poetry.org/docs/)

### Running Bagel

If all dependencies are installed locally for reading robologs, Bagel should be ready to go:

```sh
poetry install
poetry run python3 main.py --help
```

If you prefer not to install robotics-related dependencies locally, you can run Bagel in an isolated Docker container. We provide [Docker images](./compose.yaml) for supported log formats — using ROS 2 Kilted as an example:

Make sure to mount your local robolog data to the container in the compose.yaml file:

```yaml
services:
  ros2-kilted:
    ...
    volumes:
      - /local/path/to/robolog:/home/ubuntu/data/robolog
```

Then, spin up the Bagel web app:

```sh
docker compose -f compose.yaml build ros2-kilted
docker compose -f compose.yaml up ros2-kilted
```
