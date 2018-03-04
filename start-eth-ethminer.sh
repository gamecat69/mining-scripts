#!/bin/bash

#   ---------------------
#   Pre-reqs
#   ---------------------

#   ----------------
#   Set variables
#   ----------------

SERVER=http://eth1.nanopool.org:8888
FSERVER=http://eth-eu2.nanopool.org:9999
WALLET=0x75A3CdA475EE196916ec76C7174eCd7886163beC
WORKER=gtx-1060x6-2-ethminer
EMAIL=nikansell00@gmail.com
MININGCMD="/home/mining/ethminer/bin/ethminer --opencl -U -F $SERVER/$WALLET.$WORKER/$EMAIL --farm-recheck 200 --api-port 3333"

export GPU_FORCE_64BIT_0=PTR
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

#	Kill previous process
echo "Killing previous ethminer process"
pkill -f "ethminer -U"

#   ------------------------
#   Start mining
#   ------------------------

echo $MININGCMD
$MININGCMD


