#!/bin/bash

POWERLIMIT_WATTS=100
GPUOVERCLOCK_0=100
MEMOVERCLOCK_0=700
GPUOVERCLOCK_1=100
MEMOVERCLOCK_1=700
GPUOVERCLOCK_2=100
MEMOVERCLOCK_2=700
GPUOVERCLOCK_3=100
MEMOVERCLOCK_3=700
GPUOVERCLOCK_4=100
MEMOVERCLOCK_4=700
GPUOVERCLOCK_5=226
MEMOVERCLOCK_5=900
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

echo "Overclocking GPU Clocks"

nvidia-settings --assign "[gpu:0]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_0"
nvidia-settings --assign "[gpu:1]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_1"
nvidia-settings --assign "[gpu:2]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_2"
nvidia-settings --assign "[gpu:3]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_3"
nvidia-settings --assign "[gpu:4]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_4"
nvidia-settings --assign "[gpu:5]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK_5"

#   echo "Overclocking GPU by $GPUOVERCLOCK"
#   n=0
#   while [ $n -lt $NUMGPU ];
#   do
#      nvidia-settings --assign "[gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK"
#      #nvidia-settings -a [gpu:${n}]/GPUGraphicsClockOffset[3]=$GPUOVERCLOCK
#      let n=n+1
#   done

fi

#   GPU Memory Overclock

if [ "$MEMOC" = "yes" ] ; then

echo "Overclocking GPU Memory"

nvidia-settings --assign "[gpu:0]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_0"
nvidia-settings --assign "[gpu:1]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_1"
nvidia-settings --assign "[gpu:2]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_2"
nvidia-settings --assign "[gpu:3]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_3"
nvidia-settings --assign "[gpu:4]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_4"
nvidia-settings --assign "[gpu:5]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK_5"

#   echo "Overclocking GPU Memory by $MEMOVERCLOCK"
#   n=0
#   while [ $n -lt $NUMGPU ];
#   do
#      nvidia-settings --assign "[gpu:${n}]/GPUMemoryTransferRateOffset[3]=$MEMOVERCLOCK"
#      #nvidia-settings -a [gpu:${n}]/GPUMemoryTransferRateOffset[2]=$MEMOVERCLOCK
#      let n=n+1
#   done

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


