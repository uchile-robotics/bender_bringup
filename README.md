# Bender Bringup

## Table of Contents

- [Bender Bringup](#bender-bringup)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Overview](#overview)
  - [Requirements](#requirements)
  - [Package Structure](#package-structure)
  - [Launch Instructions](#launch-instructions)
    - [Start the robot](#start-the-robot)
      - [Basic setup](#basic-setup)
      - [Full system](#full-system)
      - [Slam Mode](#slam-mode)
      - [Localization only](#localization-only)
      - [Navigation only](#navigation-only)
    - [Maps and Parameters](#maps-and-parameters)
    - [Notes](#notes)

## Introduction

This package provides the launch configurations, parameter files, and map resources required to bring up the **Bender robot** on **ROS 2 Jazzy**.  
It integrates the robot’s localization, navigation, and visualization systems into a unified launch structure.

---

## Overview

`bender_bringup` is responsible for starting all core subsystems of the robot, including:

- **Localization** (AMCL, SLAM Toolbox, or Cartographer)
- **Navigation** (Nav2 stack)
- **Visualization** (RViz configuration)
- **Robot bringup** (base, sensors, and full setup)

The package is structured to support different operation modes such as:

- Mapping and localization
- Full navigation with existing maps
- SLAM operation for exploration and map creation

---

## Requirements

- **ROS 2 Jazzy Jalisco**
- **Nav2** (`nav2_bringup`, `nav2_msgs`, etc.)
- **SLAM Toolbox** or **Cartographer**
- **Robot-specific packages** (`bender_description`, `bender_bringup`, `bender_bringup_interfaces`, etc.)

Remember that even though you can build this package and all its necessary dependencies directly in your pc it is **highly** recommended that you use the docker containers that are located in [uchile_system](https://github.com/uchile-robotics/uchile_system). In that package there are some instructions on how to install it properly (In that docker container you can plug-and-play)

Make sure all dependencies are properly built in your workspace:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Package Structure

```bash
bender_bringup/
├── launch/
│   ├── localization/
│   │   ├── bender_cartographer.launch.py
│   │   ├── localization_launch.py
│   │   └── slam_toolbox.launch.py
│   ├── navigation/
│   │   └── navigation_launch.py
│   ├── robot/
│   │   ├── bender_hardware.launch.py
│   │   ├── bender_navigation.launch.py
│   │   ├── bender_moveit.launch.py
│   │   └── bender_full.launch.py
│   ├── sim/
│   │   └── gazebo.launch.py
│   └── tools/rviz/bender.rviz
├── maps/
│   ├── env_30_may_2025/
│   ├── quimica/
│   └── stage_5_may_2025/
├── params/
│   ├── localization/
│   ├── maps/
│   └── navigation/
├── CMakeLists.txt
├── package.xml
└── README.md
```

| Folder                | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `launch/localization` | Launch files for localization and SLAM modes                      |
| `launch/navigation`   | Launch for the Nav2 navigation stack                              |
| `launch/robot`        | Core bringup launch files: hardware, navigation, MoveIt and all-in-one |
| `launch/sim`          | Gazebo simulation                                                 |
| `launch/tools/rviz`   | RViz configuration for visualization                              |
| `maps`                | Predefined maps with `.pgm` and `.yaml` pairs                     |
| `params`              | Parameter files for localization, navigation, and maps            |

## Launch Instructions

### Start the robot

The bringup is split so that the hardware can run on Bender's Raspberry Pi and the heavy nodes (Nav2, MoveIt) on a second computer, both on the same ROS 2 network.

#### Hardware (Raspberry Pi)

Launches `robot_state_publisher`, `ros2_control` (namespace `/bender`) with its controllers, the LiDAR, the joystick and `twist_mux`.

```bash
ros2 launch bender_bringup bender_hardware.launch.py
```

| Argument   | Default | Description                                                         |
| ---------- | ------- | ------------------------------------------------------------------- |
| `use_arms` | `true`  | Shoulders (ODrive), arms, grippers and head (Dynamixel)             |
| `use_base` | `true`  | Pioneer base, e-stop broadcaster and `twist_mux`                    |
| `use_joy`  | `true`  | Joystick teleop (only if `use_base` is true)                        |
| `use_lidar`| `true`  | RPLidar C1 and its scan filter (publishes `/scan`)                  |

```bash
# Base only
ros2 launch bender_bringup bender_hardware.launch.py use_arms:=false
# Arms only
ros2 launch bender_bringup bender_hardware.launch.py use_base:=false
```

#### Navigation

Launches localization (AMCL) and Nav2. Use `slam:=true` to build a map with slam_toolbox instead of localizing. Arguments of the included launch files (`map`, `params_file`, ...) can also be passed here.

```bash
ros2 launch bender_bringup bender_navigation.launch.py
ros2 launch bender_bringup bender_navigation.launch.py slam:=true
```

#### MoveIt

Launches `move_group` and RViz (`use_rviz:=false` to skip it). Pass `use_base:=false` if the base is not running, so the static `world -> base_link` transform is published.

```bash
ros2 launch bender_bringup bender_moveit.launch.py
```

#### Full system

Everything on a single computer: hardware, navigation (if `use_base`) and MoveIt (if `use_arms`). Accepts `use_arms`, `use_base`, `use_joy`, `use_lidar`, `use_rviz` and `slam`.

```bash
ros2 launch bender_bringup bender_full.launch.py
```

#### Simulation

```bash
ros2 launch bender_bringup gazebo.launch.py
```

#### Localization only

Useful for testing AMCL or SLAM Toolbox independently

```bash
ros2 launch bender_bringup localization_launch.py
```

#### Navigation only

Starts the Nav2 stack using the selected map and parameter configuration.

```bash
ros2 launch bender_bringup navigation_launch.py
```

### Maps and Parameters

All parameters of interest are located in the [`params`](./params) folder inside this repository. Navigation parameters can be tuned on [`params/navigation/nav2_params.yaml`](params/navigation/nav2_params.yaml). Maps are stored in [`params/maps/maps.yaml`](params/maps/maps.yaml) and selected via the configuration file.

### Notes

- This package assumes the robot’s base and sensors are already available via their respective drivers.

- The launch files are modular, allowing you to include them in higher-level launch setups if needed (e.g., navigation-only mode, mapping mode, etc.).

- To integrate with your own robot description, ensure TF tree and topic names match those expected by Nav2 and AMCL.
