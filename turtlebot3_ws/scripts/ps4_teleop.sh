#!/bin/bash

# Author: Gideon Tladi
# File Directory: /home/gideon/turtlebot3_ws/scripts/ps4_teleop.sh

ros2 run teleop_twist_joy teleop_node --ros-args \
  -p require_enable_button:=True \
  -p enable_button:=9 \
  -p enable_turbo_button:=10 \
  -p axis_linear.x:=1 \
  -p axis_angular.yaw:=2 \
  -p axis_angular.pitch:=-1 \
  -p axis_angular.roll:=-1 \
  -p scale_linear.x:=0.5 \
  -p scale_angular.yaw:=0.8 \
  -p scale_linear_turbo.x:=1.5 \
  -p scale_angular_turbo.yaw:=2.4 \
  -p axis_deadzone:=0.15

# =============================================================================
# Commented Code Snippet for Reference (Because bash does not support inline comments)
# =============================================================================
# ros2 run teleop_twist_joy teleop_node --ros-args \
#  -p require_enable_button:=True \                  # Safety Mechanism: If true, the user must hold L1 button to enable movement.
#  -p enable_button:=9 \                             # L1 button
#  -p enable_turbo_button:=10 \                      # R1 button
#  -p axis_linear.x:=1 \                             # Left Stick Up/Down
#  -p axis_angular.yaw:=2 \                          # Right Stick Left/Right
#  -p axis_angular.pitch:=-1 \                       # Disabled
#  -p axis_angular.roll:=-1 \                        # Disabled
#  -p scale_linear.x:=0.5 \                          # Max Forward/Reverse Speed (in m/s)
#  -p scale_angular.yaw:=0.8 \                       # Max Turning Speed (in rad/s)
#  -p scale_linear_turbo.x:=1.5 \                    # Max Turbo Forward/Reverse Speed (in m/s)
#  -p scale_angular_turbo.yaw:=2.4 \                 # Max Turbo Turning Speed (in rad/s)
#  -p axis_deadzone:=0.15                            # Deadzone for Joystick Inputs
# =============================================================================


# =============================================================================
# PS4 Controller Map (Verified via ros2 topic echo /joy)
# =============================================================================
#
# AXES
# ----
# axis 0   Left Stick Left/Right      Left=1.0,  Right=-1.0  (inverted)
# axis 1   Left Stick Up/Down         Up=1.0,    Down=-1.0
# axis 2   Right Stick Left/Right     Left=1.0,  Right=-1.0  (inverted)
# axis 3   Right Stick Up/Down        Up=1.0,    Down=-1.0
# axis 4   L2 Trigger                 Rest=1.0,  Fully pressed=-1.0
# axis 5   R2 Trigger                 Rest=1.0,  Fully pressed=-1.0
#
# Note: L2 and R2 are axes, not buttons. They cannot be used as
#       enable_button or enable_turbo_button.
#
# BUTTONS
# -------
# button 0    Cross
# button 1    Circle
# button 2    Square
# button 3    Triangle
# button 4    Share
# button 5    PS Button
# button 6    Options
# button 7    L3 (Left Stick Click)
# button 8    R3 (Right Stick Click)
# button 9    L1
# button 10   R1
# button 11   D-Pad Up
# button 12   D-Pad Down
# button 13   D-Pad Left
# button 14   D-Pad Right
# button 15   Touchpad Click          Same index regardless of click position
#
# =============================================================================
