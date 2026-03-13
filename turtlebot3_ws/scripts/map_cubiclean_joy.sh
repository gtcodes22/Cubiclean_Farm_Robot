#!/bin/bash

# Author: Gideon Tladi

# Kill any old session
tmux kill-session -t cubiclean_mapping_joy 2>/dev/null

# Start tmuxinator
tmuxinator start cubiclean_mapping_joy