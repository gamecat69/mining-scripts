#!/bin/bash

#    Resets wifi adapter if connection drops

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

RED='\033[0;31m'
YELLOW='\033[0;93m'
NC='\033[0m' # No Color

while [ 1 = 1 ]
do

   if ping -c 1 $HOST_TO_PING >/dev/null 2>&1 ; then
      echo -e "${NC}[WIFI MON] Network up"
   else
      echo -e "${RED}[WIFI MON] Network down, resetting wifi card${NC}"
      nmcli radio wifi off
      nmcli radio wifi on
      sleep 5
      ./pushover.sh "$MINERNAME" "Network down, resetting wifi card"
   fi

   sleep 60

done
