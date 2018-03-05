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

POWERLIMIT_WATTS[0]=`readJson config.json POWERLIMIT_WATTS_0`
POWERLIMIT_WATTS[1]=`readJson config.json POWERLIMIT_WATTS_1`
POWERLIMIT_WATTS[2]=`readJson config.json POWERLIMIT_WATTS_2`
POWERLIMIT_WATTS[3]=`readJson config.json POWERLIMIT_WATTS_3`
POWERLIMIT_WATTS[4]=`readJson config.json POWERLIMIT_WATTS_4`
POWERLIMIT_WATTS[5]=`readJson config.json POWERLIMIT_WATTS_5`
POWERLIMIT_WATTS[6]=`readJson config.json POWERLIMIT_WATTS_6`
POWERLIMIT_WATTS[7]=`readJson config.json POWERLIMIT_WATTS_7`
LIMITPOWER=`readJson config.json LIMITPOWER`

#	Run this from /etc/rc.local as it needs root access

NUMGPU="$(nvidia-smi -L | wc -l)"
echo "[NVIDIA-OC] Found $NUMGPU Nvidia cards"

if [ "$LIMITPOWER" = "yes" ] ; then

   n=0
   while [ $n -lt $NUMGPU ];
   do
      echo "[NVIDIA-OC] Limiting  GPU:$n power to ${POWERLIMIT_WATTS[$n]}"
      nvidia-smi -i $n -pm 1
      nvidia-smi -i $n -pl ${POWERLIMIT_WATTS[$n]}
      let n=n+1
   done

fi


