#!/bin/bash

#	--------------------------------------------------
#   Resets wifi adapter if connection drops
#	Only resets adapter after MAX_ERRORS subsequent failures
#	--------------------------------------------------

SCRIPT_NAME="WIFi-MON"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

HOST_TO_PING=`readJson config.json HOST_TO_PING`
MINERNAME=`readJson config.json MINERNAME`

#	Manual entries for debugging purposes
#HOST_TO_PING='www.google.com'
#MINERNAME='itsmetheminer'

NUM_ERRORS=0
MAX_ERRORS=3
SLEEPTIME=8
ITERATIONS=0

while [ 1 = 1 ]
do

   if ping -c 1 $HOST_TO_PING >/dev/null 2>&1 ; then
      output "$GREEN" "[i] Network up"
      #	Reset Error count
      NUM_ERRORS=0
   else
      let NUM_ERRORS+=1
      output "$RED" "[w] Network down. Num errors: $NUM_ERRORS"
      
      if [ $NUM_ERRORS -ge $MAX_ERRORS ]; then 
         output "$RED" "[e] Network down, resetting wifi card${NC}"
      	 nmcli radio wifi off
      	 nmcli radio wifi on
      	 sleep 5
      	 ./pushover.sh "$MINERNAME" "Network down, resetting wifi card"
      	 #	Reset Error count
      	 NUM_ERRORS=0
      fi
      
   fi

   let ITERATIONS+=1

   #	Rotate log after 100 iterations
   if [ $ITERATIONS -ge 500 ]; then
      output "" "[i] Rotating log file"
      rotateLog $SCRIPT_NAME
      ITERATIONS=0
   fi

   sleep $SLEEPTIME

done
