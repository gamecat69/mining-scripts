#!/bin/bash

#	Set this for every script
SCRIPT_NAME="KILLMINER"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Kill any previous processes
output "" "[i] Killing cminer"
pkill -f ethdcrminer64

output "" "[i] Killing ethminer"
pkill -f ethminer

output "" "[i] Killing zminer"
pkill -f "zm --server"

output "" "[i] Killing NVIDIA logging"
pkill -f nvidia-mon

output "" "[i] Killing xmr-stak"
pkill -f xmr-stak

output "" "[i] Killing wifi-mon"
pkill -f wifi-mon

output "" "[i] Killing min-mon"
pkill -f min-mon
