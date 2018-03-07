#!/bin/bash

SCRIPT_NAME="MIN-MON"

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

function output {

	NOW=$(date +"%d-%m-%Y %T")
	echo -e "$NOW [$SCRIPT_NAME] $@"

}

WORKINGDIR=/home/mining/mining-scripts
cd $WORKINGDIR

RED='\033[0;31m'
YELLOW='\033[0;93m'
NC='\033[0m' # No Color
RUN_MODE=$1

MINMON_INT_SECS=`readJson config.json MINMON_INT_SECS`
MINMON_DELAY_SECS=`readJson config.json MINMON_DELAY_SECS`

#	Call the python script in a loop

while [ 1 = 1 ]
do

   if [ "$RUN_MODE" == "boot" ]; then
      output "${YELLOW}Just booted. Sleeping for $MINMON_DELAY_SECS secs"
      RUN_MODE=''
      sleep $MINMON_DELAY_SECS
   fi

   output "${YELLOW}Getting Mining Stats"
   python min-mon.py
   output "${YELLOW}Sleeping for $MINMON_INT_SECS${NC}"
   sleep $MINMON_INT_SECS

done
