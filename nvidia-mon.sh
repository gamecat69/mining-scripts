#!/bin/bash

SCRIPT_NAME="NVIDIA-MON"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

OUTFILE=`readJson config.json OUTFILE`
QUERYCOLUMNS=`readJson config.json QUERYCOLUMNS`
WAITTIMESECS=`readJson config.json WAITTIMESECS`
MAXHOURSPERLOG=`readJson config.json MAXHOURSPERLOG`

OUTFILE="$LOGDIR/$OUTFILE"

#   Calc when to cycle log file
MAXITERATIONS=$((3600/$WAITTIMESECS*$MAXHOURSPERLOG))

output "" "[i] Writing to $OUTFILE every $WAITTIMESECS secs"

#   Init logfile
echo $QUERYCOLUMNS > $OUTFILE

i=1
while [ 1=1 ]
do

   #   Cycle log file if max reached
   if [ $i = $MAXITERATIONS ] ; then
      output "$BLUE" "[i] Cycling logfile"
      cp $OUTFILE $OUTFILE.old
      rm $OUTFILE
      i=1
   fi

   nvidia-smi --format=noheader,csv,nounits --query-gpu=$QUERYCOLUMNS >> $OUTFILE
   sleep $WAITTIMESECS
   let i=$i+1
   REMAININGITERATIONS=$(($MAXITERATIONS - $i))

done
