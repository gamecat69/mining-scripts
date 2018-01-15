#!/bin/bash

#   ---------------------
#   Pre-reqs
#   ---------------------

#   Before running this script do the following to allow nvidia tweaks
#   sudo nvidia-xconfig --enable-all-gpus
#   sudo nvidia-xconfig --cool-24=bits
#   reboot

#   To run this script as a service:

#vi /lib/systemd/system/ethminer.service

#[Unit]
#Description=Ethminer mining daemon
#After=network.target

#[Service]
#User=mining
#Group=mining
#WorkingDirectory=/home/mining/ethminer
#Type=simple
#ExecStart=/home/mining/ethminer/start.sh
#GuessMainPID=no

#[Install]
#WantedBy=multi-user.target

#systemctl daemon-reload
#systemctl enable ethminer
#systemctl start ethminer

#To follow progress :
#journalctl -fa -u ethminer

#   ----------------
#   Set variables
#   ----------------

SERVER=http://eth1.nanopool.org:8888
FSERVER=http://eth-eu2.nanopool.org:9999
WALLET=0x75A3CdA475EE196916ec76C7174eCd7886163beC
WORKER=gtx-1060x4-ethminer
EMAIL=nikansell00@gmail.com
POWERLIMIT_WATTS=78
GPUOVERCLOCK=107
MEMOVERCLOCK=935
LIMITPOWER='yes'
MININGCMD="ethminer -G -F $SERVER/$WALLET.$WORKER/$EMAIL --farm-recheck 200"

#export GPU_FORCE_64BIT_0=PTR
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

if [ $LIMITPOWER = 'yes' ] ; then

   echo "Limiting power to $POWERLIMIT_WATTS"
   sudo nvidia-smi -pm 1
   sudo nvidia-smi -pl $POWERLIMIT_WATTS

fi

#   GPU Overlock

if [ $GPUOVERCLOCK = 'yes' ] ; then

   echo "Overclocking GPU by $GPUOVERCLOCK"
   n=0
   while [ $n -lt $NUMGPU ];
   do
      nvidia-settings -a [gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK
      let n=n+1
   done

fi

#   GPU Memory Overclock

if [ $GPUMEMOVERCLOCK = 'yes' ] ; then

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

echo $MININGCMD
$MININGCMD


