#!/bin/bash

# Kill any old session
tmux kill-session -t cubiclean_autonav 2>/dev/null

# Start tmuxinator
tmuxinator start cubiclean_autonav