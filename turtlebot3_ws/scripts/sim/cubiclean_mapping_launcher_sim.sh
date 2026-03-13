#!/bin/bash

# Kill any old session
tmux kill-session -t sim_cubiclean_mapping 2>/dev/null

# Start tmuxinator
tmuxinator start sim_cubiclean_mapping