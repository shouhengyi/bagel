<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./doc/assets/bagel_logo_dark_mode.png">
    <img src="./doc/assets/bagel_logo_light_mode.png" alt="Bagel Logo">
  </picture>
</p>

---

# Bagel - Next Generation Toolchain for Robotics 

Robotics is hard....We're here to help. We know the next generation of robotics is going to need a next generation of tools to solve the next generation of problems. Robots generate a torrent of sensor data, and our ability to process it is falling behind. We know the pain of trying to upload massive datasets from the field. 

To deal with this the robotics developers have the following (bad) options:

- 🗑️ **Drop data** and hope you don't need it later.
- ✂️ **Snip logs** based on guesswork and miss the unknown unknowns.
- 💸 **Pay a fortune** in transfer and storage costs to keep everything.


 On top of it all, we have a lot of great agentic tools, but almost none of them directed and helping the industry solve it's proble,s. 

 That's why we built Bagel. Edge first data processing and intelligence to help solve your most pressing problems. Use your fleet's downtime to aggregate analytics, train models, and auto-triage issues right at the source. With Bagel, you only send the valuable, distilled insights to the cloud, not the raw firehose of data. Use MCP to interact with your robots and data like never before.


## Agentic AI + Robotics Toolchain to solve your biggest challenges. 

Bagel lets you ask extract, transform and leverage your robotics data super easily. But even more than that, you now interact with your robots and your robotics data in natural langauge.

We turn every robot into a an MCP server to let you manage, analyze and troubleshoot your robots with the latest AI tools. 

[Read more about MCP here!](https://modelcontextprotocol.io/docs/getting-started/intro)

Use the web app to look at your data, or ask quesions and get answers

However you want to work - Bagel wants to work with you! 


## Get Started


[Get started today](#getting-started)

[Join our Discord server](https://discord.gg/KVKEmq3A)

### A Sneak Peek


Bagel allows you to extract, transform, and analyze robotics data — fast.

How fast? Cast topic messages to a **pandas `DataFrame`** or **PyArrow `Dataset`** in under four lines of code.

```py
from src.reader import factory

reader = factory.make_topic_message_reader("./doc/tutorials/data/ros2")
ds = reader.read(["/fluid_pressure"])  # return a pyarrow Dataset
df = ds.to_table().to_pandas()         # cast into a pandas DataFrame
```

You can do much more! Whether you're performing granular robot-level troubleshooting, analyzing fleet-wide performance metrics, or creating high-level executive dashboards, Bagel gets the job done.


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
- [MCP Tutorial - Claude Code](./doc/tutorials/mcp/0_claude_code_px4.ipynb)
- [MCP Tutorial - Gemini](./doc/tutorials/mcp/1_gemini_cli_ros2.ipynb)

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

Your local robolog files will be accessible inside the container at `/home/ubuntu/data`.

#### Launch the Bagel Webapp

Build and start the Bagel webapp in a container with with this command.

```sh
docker compose up --build ros2-kilted
```

#### Launch the MCP Server

Build and start the Bagel MCP server in a container with this command.

```sh
docker compose run --build --service-ports ros2-kilted uv run main.py up mcp
```

### Running Locally 🛠️

If local dependencies like ROS are already installed, you can run Bagel directly on your machine.

#### Prerequisites

First, ensure you have the following tools installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

#### Install & Source Dependencies

Next, use `uv` to install the project dependencies. We are using ROS2 Kilted as example.

```sh
source /opt/ros/kilted/setup.sh  # needed for ROS2

uv sync --group ros2
```

#### Launch the Bagel Webapp

```sh
uv run main.py up webapp
```

#### Launch the MCP Server

```sh
uv run main.py up mcp
```
