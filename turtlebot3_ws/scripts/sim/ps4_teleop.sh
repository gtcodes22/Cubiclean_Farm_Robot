#!/bin/bash

# Author: Gideon Tladi

# /home/gideon/turtlebot3_ws/scripts/ps4_teleop.sh

ros2 run teleop_twist_joy teleop_node --ros-args \
  -p require_enable_button:=True \                  # Safety Mechanism: Must hold L1 button to enable movement.
  -p enable_button:=9 \                             # L1 button
  -p enable_turbo_button:=10 \                      # R1 button
  -p axis_linear.x:=1 \                             # Left Stick Up/Down
  -p axis_angular.yaw:=2 \                          # Right Stick Left/Right
  -p axis_angular.pitch:=-1 \                       # Right Stick Up/Down
  -p axis_angular.roll:=-1 \                        # Right Stick Left/Right
  -p scale_linear.x:=0.5 \                          # Max Forward/Reverse Speed (in m/s)
  -p scale_angular.yaw:=0.8 \                       # Max Turning Speed (in m/s)
  -p scale_linear_turbo.x:=1.5 \                    # Max Turbo Forward/Reverse Speed (in m/s)
  -p scale_angular_turbo.yaw:=2.4 \                 # Max Turbo Turning Speed (in m/s)
  -p axis_deadzone:=0.15                            # Deadzone for Joystick Inputs

