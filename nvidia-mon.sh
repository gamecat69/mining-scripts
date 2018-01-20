#!/bin/bash

OUTFILE=~/nvidia-mon.log
#   Data to query. run "nvidia-smi --help" for more info
QUERYCOLUMNS="timestamp,index,gpu_name,gpu_bus_id,fan.speed,pstate,clocks_throttle_reasons.hw_slowdown,utilization.gpu,temperature.gpu,power.draw,clocks.gr"
WAITTIMESECS=300
MAXHOURSPERLOG=4
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

   nvidia-smi --format=noheader,csv --query-gpu=$QUERYCOLUMNS >> $OUTFILE
   sleep $WAITTIMESECS
   let i=$i+1
   REMAININGITERATIONS=$(($MAXITERATIONS - $i))
   #echo "$OUTFILE will be cycled in $REMAININGITERATIONS iterations"

done
