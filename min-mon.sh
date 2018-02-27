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

RED='\033[0;31m'
YELLOW='\033[0;93m'
NC='\033[0m' # No Color

MINMON_INT_SECS=`readJson config.json MINMON_INT_SECS`

#	Call the python script in a loop

while [ 1 = 1 ]
do

   echo -e "${YELLOW}[MIN MON] Getting Mining Stats"
   python min-mon.py
   echo -e "${YELLOW}[MIN MON] Sleeping for $MINMON_INT_SECS${NC}"
   sleep $MINMON_INT_SECS

done
