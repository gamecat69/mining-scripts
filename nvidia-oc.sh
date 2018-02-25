#!/bin/bash

POWERLIMIT_WATTS=100
GPUOVERCLOCK=110
MEMOVERCLOCK=700
GPUOC=yes
MEMOC=yes
MAXPERF=yes
LIMITPOWER=no

export GPU_FORCE_64BIT_PTR=0
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

#   ------------------------
#   Run this then reboot
#   info: http://www.ckode.dk/linux/overclocking-nvidia-graphics-card-on-linux/
#   ------------------------

#   sudo nvidia-xconfig -a --cool-bits=12

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

if [ "$GPUOC" = "yes" ] ; then

   echo "Overclocking GPU by $GPUOVERCLOCK"
   n=0
   while [ $n -lt $NUMGPU ];
   do
      nvidia-settings --assign "[gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK"
      #nvidia-settings -a [gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK
      let n=n+1
   done

fi

#   GPU Memory Overclock

if [ "$MEMOC" = "yes" ] ; then

   echo "Overclocking GPU Memory by $MEMOVERCLOCK"
   n=0
   while [ $n -lt $NUMGPU ];
   do
      nvidia-settings --assign "[gpu:${n}]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK"
      #nvidia-settings -a [gpu:${n}]/GPUMemoryTransferRateOffset[2]=$MEMOVERCLOCK
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

if [ "$MAXPERF" = "yes" ] ; then

   echo "Setting Powermizer to Prefer Max Performance"
   n=0
   while [  $n -lt  $NUMGPU ];
   do
      nvidia-settings -a [gpu:${n}]/GPUPowerMizerMode=1
      let n=n+1
   done

fi


