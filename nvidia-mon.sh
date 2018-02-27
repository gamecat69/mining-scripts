#!/bin/bash

#	-------------------------------------
#	Function to get data from json file
#	-------------------------------------

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

OUTFILE=`readJson config.json OUTFILE`
QUERYCOLUMNS=`readJson config.json QUERYCOLUMNS`
WAITTIMESECS=`readJson config.json WAITTIMESECS`
MAXHOURSPERLOG=`readJson config.json MAXHOURSPERLOG`

#OUTFILE=~/nvidia-mon.log
#QUERYCOLUMNS="timestamp,index,gpu_name,gpu_bus_id,fan.speed,pstate,clocks_throttle_reasons.hw_slowdown,utilization.gpu,temperature.gpu,power.draw,clocks.gr"
#WAITTIMESECS=300
#MAXHOURSPERLOG=4

#   Calc when to cycle log file
MAXITERATIONS=$((3600/$WAITTIMESECS*$MAXHOURSPERLOG))

echo "[NVIDIA-MON] Writing to $OUTFILE every $WAITTIMESECS secs"
echo .
#   Init logfile
echo $QUERYCOLUMNS > $OUTFILE

i=1
while [ 1=1 ]
do

   #   Cycle log file if max reached
   if [ $i = $MAXITERATIONS ] ; then
      echo "[NVIDIA-MON] Cycling logfile"
      cp $OUTFILE $OUTFILE.old
      rm $OUTFILE
      i=1
   fi

   nvidia-smi --format=noheader,csv,nounits --query-gpu=$QUERYCOLUMNS >> $OUTFILE
   sleep $WAITTIMESECS
   let i=$i+1
   REMAININGITERATIONS=$(($MAXITERATIONS - $i))
   #echo "$OUTFILE will be cycled in $REMAININGITERATIONS iterations"

done
