#!/bin/bash

LOGFILERETENTIONDAYS=1
SERVER1=eth-eu1.nanopool.org:9999
SERVER2=eth-eu2.nanopool.org:9999
WALLET=0x75A3CdA475EE196916ec76C7174eCd7886163beC
WORKER=gtx-1060x4-cminer
EMAIL=nikansell00@gmail.com
POOLPASS=x

export GPU_FORCE_64BIT_PTR=0
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

cd ~/cminer9.4

#   Delete files older than LOGFILERETENTIONDAYS
find ./*_log.txt -mtime +$LOGFILERETENTIONDAYS -exec rm {} \;

#   Init epools.txt
echo "POOL: $SERVER1, WALLET: $WALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" > epools.txt
echo "POOL: $SERVER2, WALLET: $WALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" >> epools.txt 

#   Start nvidia logging
~/mining-scripts/nvid-mon.sh &

#./ethdcrminer64 -epool eth-eu1.nanopool.org:9999 -ewal 0x75a3cda475ee196916ec76c7174ecd7886163beC.gtx-1060x4-cminer/nikansell00@gmail.com -epsw x -mode 1 -ftime 10
./ethdcrminer64 -epool $SERVER1 -ewal $WALLET.$WORKER/$EMAIL -epsw $POOLPASS -mode 1 -ftime 10
