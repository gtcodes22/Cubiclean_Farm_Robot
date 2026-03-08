#!/bin/bash
echo "Cleaning up old Gazebo and ROS2 processes..."

# Gazebo
pgrep -f gzserver >/dev/null && pkill -f gzserver >/dev/null 2>&1 || true
pgrep -f gzclient >/dev/null && pkill -f gzclient >/dev/null 2>&1 || true

# ROS2 nodes
pgrep -f ros2 >/dev/null && pkill -f ros2 >/dev/null 2>&1 || true

# ROS2 bag recording
pgrep -f ros2bag >/dev/null && pkill -f ros2bag >/dev/null 2>&1 || true

# RViz2
pgrep -f rviz2 >/dev/null && pkill -f rviz2 >/dev/null 2>&1 || true

# Foxglove bridge
pgrep -f foxglove_bridge >/dev/null && pkill -f foxglove_bridge >/dev/null 2>&1 || true

# Wait a few seconds to ensure all processes are fully terminated
sleep 3

echo "✅ Cleanup complete."