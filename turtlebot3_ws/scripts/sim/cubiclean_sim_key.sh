#!/bin/bash

# ================================
# CUBICLEAN SIMULATION LAUNCH SCRIPT
# Author: Gideon
# Description:
#   Launches the TurtleBot3 Gazebo Harmonic cubicle simulation
#   and opens a Teleop terminal for manual control.
#   Keeps terminals open and logs errors for debugging.
# ================================

# --- Terminal 1: Build & launch simulation in Gazebo ---
gnome-terminal -- bash -c "cd ~/turtlebot3_ws
colcon build --symlink-install --event-handlers console_direct+ &&
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger &&
ros2 launch turtlebot3_gazebo cubiclean_sim.launch.py
exec bash"

# --- Terminal 2: Teleop keyboard control ---
gnome-terminal -- bash -c "export TURTLEBOT3_MODEL=burger && \
ros2 run turtlebot3_teleop teleop_keyboard && \
exec bash"

