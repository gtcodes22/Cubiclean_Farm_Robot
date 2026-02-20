#!/bin/bash

PASSWORD="turtlebot"

gnome-terminal -- bash -c "
    sshpass -p '$PASSWORD' ssh cubiclean@10.126.200.132;
    exec bash"