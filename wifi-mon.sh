#!/bin/bash

#	--------------------------------------------------
#   Resets wifi adapter if connection drops
#	Only resets adapter after MAX_ERRORS subsequent failures
#	--------------------------------------------------

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

HOST_TO_PING=`readJson config.json HOST_TO_PING`
MINERNAME=`readJson config.json MINERNAME`

#	Manual entries for debugging purposes
#HOST_TO_PING='www.google.com'
#MINERNAME='itsmetheminer'

RED='\033[0;31m'
YELLOW='\033[0;93m'
NC='\033[0m' # No Color
NUM_ERRORS=0
MAX_ERRORS=3
SLEEPTIME=8

while [ 1 = 1 ]
do

   if ping -c 1 $HOST_TO_PING >/dev/null 2>&1 ; then
      echo -e "${NC}[WIFI MON] Network up"
      #	Reset Error count
      NUM_ERRORS=0
   else
      let NUM_ERRORS+=1
      echo -e "${RED}[WIFI MON] Network down. Num errors: $NUM_ERRORS"
      
      if [ $NUM_ERRORS -ge $MAX_ERRORS ]; then 
         echo -e "${RED}[WIFI MON] Network down, resetting wifi card${NC}"
      	 nmcli radio wifi off
      	 nmcli radio wifi on
      	 sleep 5
      	 ./pushover.sh "$MINERNAME" "Network down, resetting wifi card"
      	 #	Reset Error count
      	 NUM_ERRORS=0
      fi
      
   fi

   sleep $SLEEPTIME

done
