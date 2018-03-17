#!/bin/bash

#	Set this for every script
SCRIPT_NAME="KILLMINER"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#	Kill any previous processes
output "$BLUE" "[i] Killing cminer"
pkill -f ethdcrminer64

output "$BLUE" "[i] Killing ethminer"
pkill -f ethminer

output "$BLUE" "[i] Killing zminer"
pkill -f "zm --server"

output "$BLUE" "[i] Killing NVIDIA logging"
pkill -f nvidia-mon

output "$BLUE" "[i] Killing xmr-stak"
pkill -f xmr-stak

output "$BLUE" "[i] Killing wifi-mon"
pkill -f wifi-mon

output "$BLUE" "[i] Killing min-mon"
pkill -f min-mon
