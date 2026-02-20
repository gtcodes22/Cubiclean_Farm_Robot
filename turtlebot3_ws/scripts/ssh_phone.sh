#!/bin/bash

PASSWORD="turtlebot"

gnome-terminal -- bash -c "
    sshpass -p '$PASSWORD' ssh cubiclean@172.20.10.2;
    exec bash"