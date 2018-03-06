#!/bin/bash

function readJson {

	UNAMESTR=`uname`
	if [[ "$UNAMESTR" == 'Linux' ]]; then
    	SED_EXTENDED='-r'
	elif [[ "$UNAMESTR" == 'Darwin' ]]; then
    	SED_EXTENDED='-E'
	fi;

	VALUE=`grep -m 1 "\"${2}\"" ${1} | sed ${SED_EXTENDED} 's/^ *//;s/.*: *"//;s/",?//'`

	if [ ! "$VALUE" ]; then
		echo "Error: Cannot find \"${2}\" in ${1}" >&2;
		exit 1;
	else
		echo $VALUE ;
	fi;

}

WORKINGDIR=/home/mining/mining-scripts
cd $WORKINGDIR

GPUOVERCLOCK[0]=`readJson config.json GPUOVERCLOCK_0`
GPUOVERCLOCK[1]=`readJson config.json GPUOVERCLOCK_1`
GPUOVERCLOCK[2]=`readJson config.json GPUOVERCLOCK_2`
GPUOVERCLOCK[3]=`readJson config.json GPUOVERCLOCK_3`
GPUOVERCLOCK[4]=`readJson config.json GPUOVERCLOCK_4`
GPUOVERCLOCK[5]=`readJson config.json GPUOVERCLOCK_5`
GPUOVERCLOCK[6]=`readJson config.json GPUOVERCLOCK_6`
GPUOVERCLOCK[7]=`readJson config.json GPUOVERCLOCK_7`

MEMOVERCLOCK[0]=`readJson config.json MEMOVERCLOCK_0`
MEMOVERCLOCK[1]=`readJson config.json MEMOVERCLOCK_1`
MEMOVERCLOCK[2]=`readJson config.json MEMOVERCLOCK_2`
MEMOVERCLOCK[3]=`readJson config.json MEMOVERCLOCK_3`
MEMOVERCLOCK[4]=`readJson config.json MEMOVERCLOCK_4`
MEMOVERCLOCK[5]=`readJson config.json MEMOVERCLOCK_5`
MEMOVERCLOCK[6]=`readJson config.json MEMOVERCLOCK_6`
MEMOVERCLOCK[7]=`readJson config.json MEMOVERCLOCK_7`

POWERLIMIT_WATTS[0]=`readJson config.json POWERLIMIT_WATTS_0`
POWERLIMIT_WATTS[1]=`readJson config.json POWERLIMIT_WATTS_1`
POWERLIMIT_WATTS[2]=`readJson config.json POWERLIMIT_WATTS_2`
POWERLIMIT_WATTS[3]=`readJson config.json POWERLIMIT_WATTS_3`
POWERLIMIT_WATTS[4]=`readJson config.json POWERLIMIT_WATTS_4`
POWERLIMIT_WATTS[5]=`readJson config.json POWERLIMIT_WATTS_5`
POWERLIMIT_WATTS[6]=`readJson config.json POWERLIMIT_WATTS_6`
POWERLIMIT_WATTS[7]=`readJson config.json POWERLIMIT_WATTS_7`

LIMITPOWER=`readJson config.json LIMITPOWER`
GPUOC=`readJson config.json GPUOC`
MEMOC=`readJson config.json MEMOC`
MAXPERF=`readJson config.json MAXPERF`

export GPU_FORCE_64BIT_PTR=0
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100
export DISPLAY=:0
export XAUTHORITY=/var/run/lightdm/root/:0

#   ------------------------
#   Run this then reboot
#   info: http://www.ckode.dk/linux/overclocking-nvidia-graphics-card-on-linux/
#   info: https://github.com/Cyclenerd/ethereum_nvidia_miner/blob/master/files/setup.sh
#   ------------------------

#   Or for headless: sudo nvidia-xconfig -a --allow-empty-initial-configuration --cool-bits=31 --use-display-device="DFP-0" --no-connected-monitor

#   ------------------------
#   Configure Nvidia cards
#   ------------------------

NUMGPU="$(nvidia-smi -L | wc -l)"
echo "[NVIDIA-OC] Found $NUMGPU Nvidia cards"

#	Power limit

if [ "$LIMITPOWER" = "yes" ] ; then

   n=0
   while [ $n -lt $NUMGPU ];
   do
      echo "[NVIDIA-OC] Limiting  GPU:$n power to ${POWERLIMIT_WATTS[$n]}"
      $MINWATT = $(nvidia-smi --id=$n -q -d POWER | grep -Eo 'Min Power Limit\s+:\s.+' | grep -Eo '[0-9]{1,3}\.[0-9]{2}')
      echo "[NVIDIA-OC] Minimum for GPU:$n : $MINWATT Watts"
      nvidia-smi -i $n -pm 1
      nvidia-smi -i $n -pl ${POWERLIMIT_WATTS[$n]}
      let n=n+1
   done

fi

#   GPU Overlock

if [ "$GPUOC" = "yes" ] ; then

   n=0
   while [ $n -lt $NUMGPU ];
   do
      echo "[NVIDIA-OC] Overclocking GPU:$n by ${GPUOVERCLOCK[$n]}"
      nvidia-settings --assign "[gpu:${n}]/GPUGraphicsClockOffset[3]=${GPUOVERCLOCK[$n]}"
      let n=n+1
   done

fi

#   GPU Memory Overclock

if [ "$MEMOC" = "yes" ] ; then

   n=0
   while [ $n -lt $NUMGPU ];
   do
      echo "[NVIDIA-OC] Overclocking GPU:$n memory by ${MEMOVERCLOCK[$n]}"
      nvidia-settings --assign "[gpu:${n}]/GPUMemoryTransferRateOffset[3]=${MEMOVERCLOCK[$n]}"
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


