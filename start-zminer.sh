#!/bin/bash

SCRIPT_NAME="ZMINER"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

export GPU_FORCE_64BIT_0=PTR
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

BTCPSERVER=`readJson config.json BTCPSERVER`
BTCPSERVERPORT=`readJson config.json BTCPSERVERPORT`
BTCPWALLET=`readJson config.json BTCPWALLET`
WORKER=`readJson config.json MINERNAME`
EMAIL=`readJson config.json EMAIL`
POOLPASS=`readJson config.json POOLPASS`

output "$BLUE" "[i] Killing previous zminer process"
pkill -f "zm --server"
MININGCMD="/home/mining/zminer/zm --server $BTCPSERVER  --port $BTCPSERVERPORT --user $BTCPWALLET.$WORKER --telemetry --color"

output "" "[i] $MININGCMD"
$MININGCMD
