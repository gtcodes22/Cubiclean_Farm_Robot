# TurtleBot3 Autonomy Package Documentation — v0.0.8

## Overview

The **`turtlebot3_autonomy`** package is a ROS2 Python-based package designed to enable **fully autonomous waypoint navigation** on a TurtleBot3 robot using the ROS2 Navigation2 (Nav2) framework. It integrates navigation, monitoring, and telemetry publishing, and is compatible with visualization through Foxglove.

This package is the **navigation layer** of the wider **Cubiclean Farm Robot** system — a robotic platform developed to remotely sense animal bedding conditions as a means of detecting animal disease. The full system is maintained at [https://github.com/gtcodes22/Cubiclean_Farm_Robot](https://github.com/gtcodes22/Cubiclean_Farm_Robot).

**Project team:** Jade Cawley, Brandon Craddock, Spencer Jones, Rameez Shiekh, Gideon Tladi.

### Role of this package within the Cubiclean system

The TurtleBot3 autonomously navigates a pre-defined waypoint grid over animal bedding. At each waypoint it pauses, and the `data_logger()` method (currently a stub) is the integration point where chemical sensor readings are collected. The full data pipeline is:

```
Robot pauses at waypoint
  → chemical sensors read via chemical_sensor_drivers/
  → bot_get_readings.py packages the readings
  → server_main.py receives and stores data in bed_data/
  → data_viewer (Flutter app) / bed_webview display results to the operator
```

The wider repo contains the following components alongside this ROS2 workspace:

| Component | Description |
|---|---|
| `turtlebot3_ws/` | This ROS2 workspace — autonomous navigation |
| `chemical_sensor_drivers/` | Hardware drivers for onboard gas/chemical sensors |
| `bed_data/` | Stored sensor readings from bedding inspections |
| `bed_webview/` | Web dashboard for viewing bedding condition data |
| `data_viewer/` | Flutter mobile app for viewing readings (do not run on web emulator) |
| `server/` + `server_main.py` | Backend server receiving data from the robot |
| `bot_main.py` + `bot_get_readings.py` | Scripts running on the robot to collect and transmit sensor data |
| `turtlebot_client/` | Client-side code bridging the TurtleBot to the rest of the system |

The package allows the user to launch a complete autonomous mission with a single command, where the robot:

1. Starts the Nav2 navigation stack using the official TurtleBot3 burger-specific parameters.
2. Launches RViz2 with the TurtleBot3 navigation RViz config.
3. Loads a pre-defined map.
4. Automatically publishes an initial pose estimate to `/initialpose` so AMCL can localise.
5. Loads waypoints from a YAML file and navigates through them in sequence.
6. Pauses at each waypoint for data logging.
7. Monitors robot status such as battery, speed, and CPU usage.
8. Sends telemetry data to Foxglove for visualization.

The full session is launched via a **tmuxinator config** (`cubiclean_autonav.yml`) which starts four panes in parallel: Gazebo simulation, autonomous navigation, ros2bag recording, and Foxglove bridge.

---

## Package Structure

```
turtlebot3_ws/src/turtlebot3/turtlebot3_autonomy/
│
├── launch/
│   └── autonomous_nav.launch.py
├── config/
│   └── waypoints.yaml
├── maps/
│   ├── map.yaml
│   └── map.pgm
├── resource/
│   └── turtlebot3_autonomy        ← ament marker file (empty, DO NOT DELETE)
├── turtlebot3_autonomy/
│   ├── __init__.py
│   ├── waypoint_mission.py
│   ├── robot_monitor.py
│   └── utils/
│       ├── __init__.py
│       └── battery_monitor.py
├── package.xml
├── setup.py
└── setup.cfg
```

> **Note:** `resource/turtlebot3_autonomy` is an empty file that must exist on disk. It is the ament index marker that makes `ros2 launch` aware of this package. Without it, the build succeeds but `ros2 launch turtlebot3_autonomy ...` will fail with "package not found".

---

## Debug History & Known Issues Resolved

### Bug 1 — `ros2 launch` could not find `autonomous_nav.launch.py`

**Symptom:**
```
file 'autonomous_nav.launch.py' was not found in the share directory of package 'turtlebot3_autonomy'
```

**Root causes (multiple):**
- `setup.py` was missing the `resource/` ament index marker entry in `data_files` — the package was invisible to `ros2 launch`.
- `glob('launch/*.py')` was too broad.
- The launch file was named `auto_nav.launch.py` in some places and `autonomous_nav.launch.py` in others.

**Fix:** Corrected `setup.py` and standardised launch filename to `autonomous_nav.launch.py` everywhere.

---

### Bug 2 — Stale build cache referencing old launch filename

**Symptom:**
```
error: can't copy '.../build/turtlebot3_autonomy/launch/auto_nav.launch.py': doesn't exist or not a regular file
```

**Fix:**
```bash
rm ~/turtlebot3_ws/src/turtlebot3_autonomy/launch/auto_nav.launch.py
rm -rf ~/turtlebot3_ws/build/turtlebot3_autonomy
rm -rf ~/turtlebot3_ws/install/turtlebot3_autonomy
colcon build --packages-select turtlebot3_autonomy
source install/setup.bash
```

---

### Bug 3 — `TF_OLD_DATA` warnings / stale transforms on startup

**Symptom:**
```
[WARN]: TF_OLD_DATA ignoring data from the past for frame base_footprint
```

**Root cause:** Nav2 starting before Gazebo's sim clock was stable. Orphaned Gazebo GUI process from a previous session also publishing stale `/clock` and `/tf` data.

**Fix:**
- Changed startup guard in all tmuxinator panes from `/tf` to `/clock`.
- Added `sleep 5` after the scan guard in the Autonomy pane.
- Added aggressive `pkill` of all Gazebo processes + `ros2 daemon stop/start` at top of Gazebo pane.

---

### Bug 4 — `ROSBAG2_TRANSPORT` error: `/cmd_vel` has more than one type

**Symptom:**
```
[ERROR] [ROSBAG2_TRANSPORT]: Topic '/cmd_vel' has more than one type associated.
```

**Fix:** Use `--exclude-topics '/cmd_vel'` in the rosbag record command.

> **Note:** The flag is `--exclude-topics` (not `--exclude`). Using `--exclude` alone produces an "ambiguous option" error.

---

### Bug 5 — AMCL cannot localise / `map` frame does not exist

**Symptom:**
```
[WARN] [amcl]: AMCL cannot publish a pose or update the transform. Please set the initial pose...
[INFO] [global_costmap]: Timed out waiting for transform from base_link to map
```

**Root cause 5a — Wrong Nav2 launch file:** `autonomous_nav.launch.py` was calling `nav2_bringup/bringup_launch.py` directly without a `params_file`, causing AMCL to start with generic defaults instead of burger-specific params.

**Fix 5a:** Replace with `turtlebot3_navigation2/launch/navigation2.launch.py` which auto-loads `humble/burger.yaml`.

**Root cause 5b — No initial pose published:** AMCL waits for an initial pose on `/initialpose` before publishing the `map → base_link` transform.

**Fix 5b:** Added `set_initial_pose()` to `WaypointMission`, called before `waitUntilNav2Active()`. Publishes `PoseWithCovarianceStamped` to `/initialpose` five times with 0.5s delay, then waits 2s for AMCL to process.

> **Note:** Default initial pose is `(0, 0)` facing `+x`, matching the standard TurtleBot3 Gazebo spawn point. Adjust if your world spawns the robot elsewhere.

---

### Bug 6 — local_costmap dropping base_scan messages

**Symptom:**
```
[rviz2]: Message Filter dropping message: frame 'base_scan' at time X for reason
'the timestamp on the message is earlier than all the data in the transform cache'
```

**Root cause:** Nav2 starting before the laser scanner TF chain was live.

**Fix:** Added a `/scan` topic guard in the Autonomy pane before Nav2 launches:
```yaml
- "until ros2 topic echo /scan --once >/dev/null 2>&1; do sleep 1; done"
- "sleep 5"
```

> **Note:** `tf2_echo odom base_scan` was tried first but hangs indefinitely and never exits, making it unusable as a guard. `/scan` topic availability is a reliable proxy for the full TF chain being live.

---

### Bug 7 — waypoint_mission.py not executing (colcon --symlink-install breaks Python module discovery)

**Symptom:** Node launches silently, `rosout` produces no mission log messages. `ros2 param get /waypoint_mission waypoints_file` returns the correct path but navigation never starts.

**Root cause:** `colcon build --symlink-install` creates a `.egg-link` file pointing to the **build directory** (`build/turtlebot3_autonomy`), not the source directory. The build directory contains only `setup.py` and data files — not the Python module files. At runtime, `importlib` resolves the entry point through the egg-link, finds no `waypoint_mission.py` in the build directory, and silently falls back to a stale cached version (or fails to import the updated code).

**Diagnosis:**
```bash
# egg-link present instead of real .py file
find ~/turtlebot3_ws/install -path "*/turtlebot3_autonomy*"
# → lib/python3.12/site-packages/turtlebot3-autonomy.egg-link

# egg-link points to build dir, not src
cat ~/turtlebot3_ws/install/turtlebot3_autonomy/lib/python3.12/site-packages/turtlebot3-autonomy.egg-link
# → /home/gideon/turtlebot3_ws/build/turtlebot3_autonomy
```

**Fix:**
```bash
rm -rf ~/turtlebot3_ws/build/turtlebot3_autonomy
rm -rf ~/turtlebot3_ws/install/turtlebot3_autonomy
colcon build --packages-select turtlebot3_autonomy   # NO --symlink-install
source install/setup.bash

# Verify — should return a real .py file
find ~/turtlebot3_ws/install -name "waypoint_mission.py"
# → install/turtlebot3_autonomy/lib/python3.12/site-packages/turtlebot3_autonomy/waypoint_mission.py
```

> **Rule: NEVER use `--symlink-install` for ament_python packages in this workspace.** It breaks Python module discovery silently with no build error.

---

### Bug 8 — Duplicate `/waypoint_mission` nodes after restart

**Symptom:**
```
WARNING: nodes in the graph that share an exact name
/waypoint_mission
/waypoint_mission
```

**Root cause:** Previous session processes (RViz, Nav2, `robot_state_publisher`, etc.) were not fully killed before relaunching. They survived `tmux kill-session` because they were detached child processes.

**Fix:** Updated `kill_autonav` alias to kill all relevant processes by name, not just the tmux session:

```bash
alias kill_autonav='tmux kill-server 2>/dev/null; \
  pkill -9 -f "gz sim" 2>/dev/null; \
  pkill -9 -f gzserver 2>/dev/null; \
  pkill -9 -f gzclient 2>/dev/null; \
  pkill -9 -f "ruby.*gz" 2>/dev/null; \
  pkill -9 -f rviz 2>/dev/null; \
  pkill -9 -f foxglove 2>/dev/null; \
  pkill -9 -f waypoint_mission 2>/dev/null; \
  pkill -9 -f robot_monitor 2>/dev/null; \
  pkill -9 -f component_container 2>/dev/null; \
  pkill -9 -f robot_state_publisher 2>/dev/null; \
  pkill -9 -f nav2 2>/dev/null; \
  pkill -9 -f amcl 2>/dev/null; \
  sleep 2; \
  ros2 daemon stop 2>/dev/null; \
  ros2 daemon start 2>/dev/null; \
  echo "All autonav processes killed."'
```

> **Note:** Use `tmux kill-server` (not `kill-session`) to ensure all tmux sessions are terminated. After running `kill_autonav`, verify with `ros2 node list` — it should return empty or just the daemon. A `WARNING: nodes share an exact name` in `ros2 node list` after a clean restart is usually a ROS2 daemon cache artefact and not a real duplicate — confirm with `pgrep -a -f waypoint_mission` which shows actual running processes.

---

### Bug 9 — Terminal escape sequence garbage (`^[[A^[[B...`) in tmux panes

**Symptom:** Arrow key presses and mouse clicks print raw ANSI escape sequences directly to the shell in tmux panes. Commands become corrupted and unexecutable.

**Root cause:** Two separate sub-issues were found:
- `set-option -g mouse on` lines inside `cubiclean_autonav.yml` were overriding the `mouse off` setting in `~/.tmux.conf` on every session start.
- The terminal emulator (Tilix) forwards raw escape sequences when a tmux pane is in an unexpected input state.

**Fix:**
- Removed all `tmux set -g mouse on` lines from `cubiclean_autonav.yml`.
- `~/.tmux.conf` already has `mouse off` — no changes needed there.
- If a terminal pane enters a broken input state, open a **new terminal tab** (not a tmux pane) rather than trying to fix the broken one.

> **Note:** `reset` typed in the broken terminal does not reliably fix this state. A fresh terminal tab is always the fastest recovery.

---

### All Code Fixes Applied (Summary)

| # | File | Issue | Fix |
|---|---|---|---|
| 1 | `package.xml` | `<n>` tag was malformed | Corrected to `<name>turtlebot3_autonomy</name>` |
| 2 | `setup.py` | Missing ament resource marker in `data_files` | Added `share/ament_index/resource_index/packages` entry |
| 3 | `setup.py` | `glob('launch/*.py')` too broad | Changed to `glob('launch/*.launch.py')` |
| 4 | `setup.py` | `utils/` subpackage not installed | Added `turtlebot3_autonomy.utils` to `packages` list |
| 5 | `launch/` | Filename inconsistency (`auto_nav` vs `autonomous_nav`) | Standardised to `autonomous_nav.launch.py` everywhere |
| 6 | `waypoint_mission.py` | Unused import `quaternion_from_euler` | Removed |
| 7 | Package structure | `battery_monitor.py` shown at wrong directory level | Corrected to `utils/battery_monitor.py` with `utils/__init__.py` |
| 8 | `autonomous_nav.launch.py` | Called `nav2_bringup` directly, no burger params | Replaced with `turtlebot3_navigation2/navigation2.launch.py` |
| 9 | `autonomous_nav.launch.py` | Bare `rviz2` node with no config | Removed — RViz now handled by `navigation2.launch.py` |
| 10 | `waypoint_mission.py` | No initial pose published, AMCL never localised | Added `set_initial_pose()` called before `waitUntilNav2Active()` |
| 11 | `cubiclean_autonav.yml` | Startup guard waited for `/tf` not `/clock` | Changed all guards to wait for `/clock` |
| 12 | `cubiclean_autonav.yml` | Orphaned Gazebo process on restart caused stale TF | Added `pkill` + `ros2 daemon stop/start` at top of Gazebo pane |
| 13 | `cubiclean_autonav.yml` | `ros2 bag record -a` failed on `/cmd_vel` type conflict | Added `--exclude-topics '/cmd_vel'` to record command |
| 14 | `~/.tmux.conf` | Mouse on caused raw escape sequences on click | Set `mouse off` |
| 15 | `cubiclean_autonav.yml` | Nav2 starting before laser TF chain live | Added `/scan` topic guard + `sleep 5` before Nav2 launch |
| 16 | Build process | `--symlink-install` broke Python module discovery silently | Never use `--symlink-install`; always use plain `colcon build` |
| 17 | `~/.bashrc` kill_autonav | Only killed tmux session; RViz/Nav2/robot_state_publisher survived | Expanded to `pkill -9` all ROS2 and Gazebo processes by name; use `tmux kill-server` |
| 18 | `cubiclean_autonav.yml` | `tmux set -g mouse on` lines overriding `~/.tmux.conf` on every start | Removed all mouse-on lines from yml |

---

## How to Build and Launch

```bash
# NOTE: resource/turtlebot3_autonomy already exists on disk — do not delete it.

# Build (NEVER use --symlink-install)
cd ~/turtlebot3_ws
colcon build --packages-select turtlebot3_autonomy
source install/setup.bash

# Verify the install is correct
find ~/turtlebot3_ws/install -name "waypoint_mission.py"
# Must return: install/turtlebot3_autonomy/lib/python3.12/site-packages/turtlebot3_autonomy/waypoint_mission.py
# If it returns nothing, the build used --symlink-install previously — wipe and rebuild:
# rm -rf build/turtlebot3_autonomy install/turtlebot3_autonomy
# colcon build --packages-select turtlebot3_autonomy

# Launch
export TURTLEBOT3_MODEL=burger
tmuxinator start cubiclean_autonav
```

---

## Teardown

Always use `kill_autonav` — never `tmux kill-session` alone.

```bash
alias kill_autonav='tmux kill-server 2>/dev/null; \
  pkill -9 -f "gz sim" 2>/dev/null; \
  pkill -9 -f gzserver 2>/dev/null; \
  pkill -9 -f gzclient 2>/dev/null; \
  pkill -9 -f "ruby.*gz" 2>/dev/null; \
  pkill -9 -f rviz 2>/dev/null; \
  pkill -9 -f foxglove 2>/dev/null; \
  pkill -9 -f waypoint_mission 2>/dev/null; \
  pkill -9 -f robot_monitor 2>/dev/null; \
  pkill -9 -f component_container 2>/dev/null; \
  pkill -9 -f robot_state_publisher 2>/dev/null; \
  pkill -9 -f nav2 2>/dev/null; \
  pkill -9 -f amcl 2>/dev/null; \
  sleep 2; \
  ros2 daemon stop 2>/dev/null; \
  ros2 daemon start 2>/dev/null; \
  echo "All autonav processes killed."'
```

After running `kill_autonav`, verify with:
```bash
ros2 node list    # should be empty
pgrep -a gz       # should return nothing
```

---

## Tmux Config

`~/.tmux.conf`:

```ini
# Disable mouse — prevents raw escape sequences being printed on click.
# Use Ctrl+b + arrow keys to move between panes.
# Use Ctrl+b z to zoom/unzoom the current pane.
# Use Ctrl+b [ to enter scroll mode (q to exit).
set-option -g mouse off

# Prevent tmux from auto-renaming windows
set-option -g allow-rename off

# Increase scrollback buffer
set-option -g history-limit 5000
```

Apply without restarting:
```bash
tmux source-file ~/.tmux.conf
```

---

## Tmuxinator Config

`~/.config/tmuxinator/cubiclean_autonav.yml`

```yaml
name: cubiclean_autonav
root: ~/turtlebot3_ws

windows:
  - turtlebot:
      layout: tiled
      panes:
        - Gazebo:
          - "echo 'Killing leftover Gazebo/ROS2 processes...'"
          # Kill any orphaned Gazebo/ROS2 processes from a previous session.
          # Without this, stale /clock and /tf data causes TF_OLD_DATA warnings.
          - "pkill -9 -f 'gz sim' 2>/dev/null; pkill -9 -f 'gzserver' 2>/dev/null; pkill -9 -f 'gzclient' 2>/dev/null; pkill -9 -f 'ruby.*gz' 2>/dev/null; pkill -9 -f 'ros2' 2>/dev/null; true"
          - "ros2 daemon stop 2>/dev/null; sleep 2; ros2 daemon start 2>/dev/null"
          - "sleep 2"
          - "echo 'Launching Gazebo Sim with TurtleBot3 world...'"
          - "source install/setup.bash"
          - "export TURTLEBOT3_MODEL=burger"
          - "ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py use_sim_time:=True"

        - Autonomy:
          - "echo 'Launching autonomous navigation...'"
          - "source install/setup.bash"
          - "export TURTLEBOT3_MODEL=burger"
          # Guard 1: wait for sim clock to be publishing
          - "until ros2 topic echo /clock --once >/dev/null 2>&1; do sleep 1; done"
          # Guard 2: wait for /scan — confirms laser + TF chain is live
          # (prevents local_costmap from dropping scan messages on startup)
          - "until ros2 topic echo /scan --once >/dev/null 2>&1; do sleep 1; done"
          # Extra buffer for TF to stabilise before Nav2 starts
          - "sleep 5"
          - "ros2 launch turtlebot3_autonomy autonomous_nav.launch.py use_sim_time:=True"

        - Ros2bag:
          - "cd ~/turtlebot3_ws/ros2bags"
          - "source ../install/setup.bash"
          - "until ros2 topic echo /clock --once >/dev/null 2>&1; do sleep 1; done"
          # --exclude-topics '/cmd_vel' avoids ROSBAG2_TRANSPORT type conflict error.
          # /cmd_vel is published with conflicting types by different nodes.
          - "ros2 bag record --exclude-topics '/cmd_vel' -a -o cubiclean_autonav_$(date +%Y%m%d_%H%M%S)"

        - Foxglove:
          - "source install/setup.bash"
          - "export TURTLEBOT3_MODEL=burger"
          - "until ros2 topic echo /clock --once >/dev/null 2>&1; do sleep 1; done"
          - "ros2 launch foxglove_bridge foxglove_bridge_launch.xml"

attach: true
```

---

## File Contents

### 1. `package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">

  <name>turtlebot3_autonomy</name>
  <version>0.0.1</version>
  <description>
    Autonomous navigation package for TurtleBot3 using Nav2 waypoint missions
  </description>

  <maintainer email="myemail@gmail.com">My Name</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>launch</exec_depend>
  <exec_depend>launch_ros</exec_depend>
  <exec_depend>nav2_bringup</exec_depend>
  <exec_depend>nav2_simple_commander</exec_depend>
  <exec_depend>turtlebot3_navigation2</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>nav_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>visualization_msgs</exec_depend>

  <exec_depend>tf_transformations</exec_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>

</package>
```

---

### 2. `setup.py`

```python
from setuptools import setup
import os
from glob import glob

package_name = 'turtlebot3_autonomy'

setup(
    name=package_name,
    version='0.0.1',
    packages=[
        package_name,
        package_name + '.utils',        # required to install the utils subpackage
    ],
    data_files=[
        # ament package index marker — required for ros2 launch to find this package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files into the share directory
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        # Install config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        # Install map files
        (os.path.join('share', package_name, 'maps'),
            glob('maps/*.yaml') + glob('maps/*.pgm')),
    ],
    install_requires=['setuptools', 'psutil'],
    zip_safe=True,
    maintainer='My Name',
    maintainer_email='myemail@gmail.com',
    description='Autonomous waypoint navigation for TurtleBot3',
    license='Apache 2.0',
    entry_points={
        'console_scripts': [
            'waypoint_mission = turtlebot3_autonomy.waypoint_mission:main',
            'robot_monitor = turtlebot3_autonomy.robot_monitor:main',
        ],
    },
)
```

---

### 3. `setup.cfg`

```ini
[develop]
script_dir=$base/lib/turtlebot3_autonomy
[install]
install_scripts=$base/lib/turtlebot3_autonomy
```

---

### 4. `launch/autonomous_nav.launch.py`

```python
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_tb3_nav2 = get_package_share_directory('turtlebot3_navigation2')
    pkg_autonomy = get_package_share_directory('turtlebot3_autonomy')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    map_file_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_autonomy, 'maps', 'map.yaml'),
        description='Full path to map yaml'
    )

    waypoints_file_arg = DeclareLaunchArgument(
        'waypoints_file',
        default_value=os.path.join(pkg_autonomy, 'config', 'waypoints.yaml'),
        description='Full path to waypoints yaml'
    )

    use_sim_time   = LaunchConfiguration('use_sim_time')
    map_file       = LaunchConfiguration('map')
    waypoints_file = LaunchConfiguration('waypoints_file')

    # Use the official TurtleBot3 navigation2 launch instead of raw nav2_bringup.
    # This loads burger-specific Nav2 params and the correct RViz config.
    # Using nav2_bringup directly (without params_file) causes AMCL to start with
    # generic defaults, preventing localisation and blocking all navigation.
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tb3_nav2, 'launch', 'navigation2.launch.py')
        ),
        launch_arguments={
            'map': map_file,
            'use_sim_time': use_sim_time,
        }.items()
    )

    mission_node = Node(
        package='turtlebot3_autonomy',
        executable='waypoint_mission',
        name='waypoint_mission',
        parameters=[{
            'use_sim_time': use_sim_time,
            'waypoints_file': waypoints_file,
        }],
        output='screen'
    )

    monitor_node = Node(
        package='turtlebot3_autonomy',
        executable='robot_monitor',
        name='robot_monitor',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        map_file_arg,
        waypoints_file_arg,
        nav2_launch,
        mission_node,
        monitor_node,
    ])
```

---

### 5. `turtlebot3_autonomy/waypoint_mission.py`

```python
#!/usr/bin/env python3

import os
import yaml
import time
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from ament_index_python.packages import get_package_share_directory


class WaypointMission(Node):

    def __init__(self):
        super().__init__('waypoint_mission')

        self.declare_parameter(
            'waypoints_file',
            os.path.join(
                get_package_share_directory('turtlebot3_autonomy'),
                'config',
                'waypoints.yaml'
            )
        )

        self.navigator = BasicNavigator()
        self.waypoints = self.load_waypoints()
        self.get_logger().info(f"Loaded {len(self.waypoints)} waypoints")

        # Run the mission in a separate thread so rclpy.spin()
        # can process callbacks (Nav2 feedback, TF, etc.) concurrently.
        self._mission_thread = threading.Thread(
            target=self.run_mission, daemon=True
        )
        self._mission_thread.start()

    def load_waypoints(self):
        waypoints_file = self.get_parameter('waypoints_file').value
        self.get_logger().info(f"Loading waypoints from: {waypoints_file}")

        with open(waypoints_file) as f:
            data = yaml.safe_load(f)

        waypoints = []
        for name, wp in data['waypoints'].items():
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()

            pose.pose.position.x = float(wp['pose'][0])
            pose.pose.position.y = float(wp['pose'][1])
            pose.pose.position.z = float(wp['pose'][2])

            # orientation stored as [w, x, y, z]
            pose.pose.orientation.w = float(wp['orientation'][0])
            pose.pose.orientation.x = float(wp['orientation'][1])
            pose.pose.orientation.y = float(wp['orientation'][2])
            pose.pose.orientation.z = float(wp['orientation'][3])

            waypoints.append(pose)
            self.get_logger().info(
                f"  Loaded {name}: ({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})"
            )

        return waypoints

    def set_initial_pose(self):
        """
        Publish an initial pose estimate to /initialpose so AMCL can localise
        and begin publishing the map -> base_link transform that Nav2 requires.

        Pose is set to the origin (0, 0, facing +x) which matches the default
        TurtleBot3 Gazebo spawn point. Adjust x/y/orientation if your world
        spawns the robot elsewhere.
        """
        self.get_logger().info('Publishing initial pose to /initialpose...')

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0

        # Standard covariance values used by the RViz2 2D Pose Estimate tool
        msg.pose.covariance[0]  = 0.25
        msg.pose.covariance[7]  = 0.25
        msg.pose.covariance[35] = 0.06853891945200942

        pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

        # Publish several times — AMCL may not be subscribed on the first attempt
        for i in range(5):
            msg.header.stamp = self.get_clock().now().to_msg()
            pub.publish(msg)
            self.get_logger().info(f'  Initial pose publish {i + 1}/5')
            time.sleep(0.5)

        self.get_logger().info('Initial pose sent — waiting for AMCL to localise...')
        time.sleep(2.0)

    def data_logger(self, i):
        self.get_logger().info(f"Logging data at waypoint {i}")

    def run_mission(self):
        # Publish initial pose first so AMCL establishes the map->base_link
        # transform before the Nav2 activation check. Without this, Nav2 times
        # out waiting for the transform and never becomes active.
        self.set_initial_pose()

        self.navigator.waitUntilNav2Active()
        self.get_logger().info("Nav2 is active — starting mission")

        for i, waypoint in enumerate(self.waypoints):
            # Refresh the timestamp immediately before sending each goal
            waypoint.header.stamp = self.get_clock().now().to_msg()

            self.get_logger().info(f"Navigating to waypoint {i}")
            self.navigator.goToPose(waypoint)

            while not self.navigator.isTaskComplete():
                time.sleep(0.5)

            result = self.navigator.getResult()
            self.get_logger().info(f"Waypoint {i} result: {result}")
            self.data_logger(i)
            time.sleep(15)

        self.get_logger().info("Mission complete")


def main():
    rclpy.init()
    node = WaypointMission()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### 6. `turtlebot3_autonomy/robot_monitor.py`

```python
#!/usr/bin/env python3

import math
import psutil

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, Bool


class RobotMonitor(Node):

    def __init__(self):
        super().__init__('robot_monitor')

        self.battery_percent = None
        self.robot_speed = 0.0

        self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.battery_pub     = self.create_publisher(Float32, '/robot/battery_percent', 10)
        self.speed_pub       = self.create_publisher(Float32, '/robot/speed', 10)
        self.cpu_pub         = self.create_publisher(Float32, '/robot/cpu_usage', 10)
        self.low_battery_pub = self.create_publisher(Bool,   '/robot/battery_low', 10)

        self.create_timer(1.0, self.publish_status)
        self.get_logger().info('Robot monitor started')

    def battery_callback(self, msg):
        self.battery_percent = msg.percentage

    def odom_callback(self, msg):
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        self.robot_speed = math.sqrt(vx ** 2 + vy ** 2)

    def publish_status(self):
        if self.battery_percent is not None:
            msg = Float32()
            msg.data = float(self.battery_percent)
            self.battery_pub.publish(msg)

        speed = Float32()
        speed.data = float(self.robot_speed)
        self.speed_pub.publish(speed)

        cpu = Float32()
        cpu.data = float(psutil.cpu_percent())
        self.cpu_pub.publish(cpu)

        low = Bool()
        low.data = (self.battery_percent is not None) and (self.battery_percent < 0.25)
        self.low_battery_pub.publish(low)


def main():
    rclpy.init()
    node = RobotMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### 7. `turtlebot3_autonomy/utils/battery_monitor.py`

```python
#!/usr/bin/env python3

from sensor_msgs.msg import BatteryState

LOW_BATTERY_THRESHOLD = 0.25


class BatteryMonitor:
    """
    Utility class for monitoring battery state.
    Subscribes to /battery_state and exposes the current percentage
    and a low-battery check method.
    """

    def __init__(self, node):
        self.node = node
        self.percent = None

        node.create_subscription(
            BatteryState,
            '/battery_state',
            self._callback,
            10
        )

    def _callback(self, msg):
        self.percent = msg.percentage

    def battery_low(self):
        if self.percent is None:
            return False
        return self.percent < LOW_BATTERY_THRESHOLD

    def get_percent(self):
        return self.percent
```

---

### 8. `config/waypoints.yaml`

```yaml
waypoints:
  waypoint0:
    pose:
      - 1.4166452884674072
      - -0.05518263578414917
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint1:
    pose:
      - 1.4427535533905029
      - -1.1376404762268066
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint2:
    pose:
      - 2.4732513427734375
      - -0.99568420648574829
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint3:
    pose:
      - 2.635441780090332
      - -0.082296192646026611
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint4:
    pose:
      - 2.6305596828460693
      - 1.0420876741409302
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint5:
    pose:
      - 1.4955624341964722
      - 1.0162422657012939
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint6:
    pose:
      - 0.1714775562286377
      - 1.0018510818481445
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
  waypoint7:
    pose:
      - 0.14530956745147705
      - -0.027805536985397339
      - 0
    orientation:
      - 1
      - 0
      - 0
      - 0
```

---

## Telemetry Topics (Foxglove)

| Topic | Type | Description |
|---|---|---|
| `/robot/battery_percent` | `Float32` | Current battery percentage |
| `/robot/speed` | `Float32` | Current robot speed (m/s) |
| `/robot/cpu_usage` | `Float32` | CPU usage of host (%) |
| `/robot/battery_low` | `Bool` | True if battery < 25% |

---

## Future Enhancements

- Sensor data logging at each waypoint (currently a stub in `data_logger()`).
- Battery-aware mission abort / return-to-dock.
- Waypoint visualisation markers in RViz.
- Aggregated `/robot_health` topic combining battery, speed, and CPU.
- Integration with additional sensors (camera, lidar) for per-waypoint telemetry.
