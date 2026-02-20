#!/bin/bash

# this tells to shell to exit if any command returns a non zero exit status 
# non-zero error is an indication of failure in Unix systems
set -e

# this two commands will source the overlay and underlay
# such that we can run our package 
source /opt/ros/jazzy/setup.bash
source /app/turtlebot3_ws/install/setup.bash

# This means that we are doing everything in this  entrypoint.sh script, 
# then in the same shell, we will run the command the user passes in on the command line.
# (if the use passes a command)
exec "$@"