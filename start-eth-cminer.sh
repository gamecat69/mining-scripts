#!/bin/bash

LOGFILERETENTIONDAYS=1
SERVER1=eth-eu1.nanopool.org:9999
SERVER2=eth-eu2.nanopool.org:9999
WALLET=0x75A3CdA475EE196916ec76C7174eCd7886163beC
WORKER=gtx-1060x4-cminer
EMAIL=nikansell00@gmail.com
POOLPASS=x
POWERLIMIT_WATTS=78
GPUOVERCLOCK=107
MEMOVERCLOCK=935
LIMITPOWER='yes'
#CMINERDIR="cminer9.4"
CMINERDIR="cminer10.0"
MININGCMD="./ethdcrminer64 -epool $SERVER1 -ewal $WALLET.$WORKER/$EMAIL -epsw $POOLPASS -mode 1 -ftime 10 -ttli 80"

#export GPU_FORCE_64BIT_PTR=0
#export GPU_MAX_HEAP_SIZE=100
#export GPU_USE_SYNC_OBJECTS=1
#export GPU_MAX_ALLOC_PERCENT=100
#export GPU_SINGLE_ALLOC_PERCENT=100

#   ------------------------
#   Configure Nvidia cards
#   ------------------------

NUMGPU="$(nvidia-smi -L | wc -l)"

#   Power Limit
#   Commented out as this needs root
#   .. will figure this out later

if [ "$LIMITPOWER" = "yes" ] ; then

   echo "Limiting power to $POWERLIMIT_WATTS Watts"
   sudo nvidia-smi -pm 1
   sudo nvidia-smi -pl $POWERLIMIT_WATTS

fi

#   GPU Overlock

if [ "$GPUOVERCLOCK" = "yes" ] ; then

   echo "Overclocking GPU by $GPUOVERCLOCK"
   n=0
   while [ $n -lt $NUMGPU ];
   do
      nvidia-settings -a [gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK
      let n=n+1
   done

fi

#   GPU Memory Overclock

if [ "$GPUMEMOVERCLOCK" = "yes" ] ; then

   echo "Overclocking GPU Memory"
   n=0
   while [ $n -lt $NUMGPU ];
   do
      nvidia-settings -a [gpu:${n}]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK
      let n=n+1
   done

fi

#   Set fan speed to auto

#n=0
#while [  $n -lt  $NUMGPU ];
#do
#    nvidia-settings -a [gpu:${n}]/GPUFanControlState=0
#    let n=n+1
#done

#   Set max performance mode

#n=0
#while [  $n -lt  $NUMGPU ];
#do
#    nvidia-settings -a [gpu:${n}]/GPUPowerMizerMode=1
#    let n=n+1
#done

#   ------------------------
#   Start mining
#   ------------------------

cd ~/$CMINERDIR

#   Delete files older than LOGFILERETENTIONDAYS
find ./*_log.txt -mtime +$LOGFILERETENTIONDAYS -exec rm {} \;

#   Init epools.txt
echo "POOL: $SERVER1, WALLET: $WALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" > epools.txt
echo "POOL: $SERVER2, WALLET: $WALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" >> epools.txt 

#   Start nvidia logging
~/mining-scripts/nvid-mon.sh &

echo $MININGCMD
$MININGCMD

#./ethdcrminer64 -epool eth-eu1.nanopool.org:9999 -ewal 0x75a3cda475ee196916ec76c7174ecd7886163beC.gtx-1060x4-cminer/nikansell00@gmail.com -epsw x -mode 1 -ftime 10 -ttli 80
#./ethdcrminer64 -epool $SERVER1 -ewal $WALLET.$WORKER/$EMAIL -epsw $POOLPASS -mode 1 -ftime 10 -ttli 80
