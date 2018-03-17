#!/bin/bash

SCRIPT_NAME="MIN-MON"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Create logdir if needed
mkdir -p "$WORKINGDIR/logs"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

RUN_MODE=$1
INTERATIONS=0

MINMON_INT_SECS=`readJson config.json MINMON_INT_SECS`
MINMON_DELAY_SECS=`readJson config.json MINMON_DELAY_SECS`

#	Call the python script in a loop

while [ 1 = 1 ]
do

   if [ "$RUN_MODE" == "boot" ]; then
      output "$BLUE" "[i] Just booted. Sleeping for $MINMON_DELAY_SECS secs"
      RUN_MODE=''
      sleep $MINMON_DELAY_SECS
   fi

   output "" "[i] Getting Mining Stats"
   python min-mon.py | tee $LOGFILE
   output "" "[i] Sleeping for $MINMON_INT_SECS${NC}"
   let INTERATIONS+=1
   
   #	Rotate log after 10 interations
   if [ $INTERATIONS -ge 2 ]; then
      output "" "[i] Rotating log file"
      rotateLog $SCRIPT_NAME
      INTERATIONS=0
   fi

   sleep $MINMON_INT_SECS

done
