#!/bin/bash

#	------------------
#	Common variables
#	------------------

WORKINGDIR="/home/mining/mining-scripts"
LOGDIR="$WORKINGDIR/logs"
CONFIG_FILE="../config-sample.json"

#	------------------
#	Common functions 
#	------------------

function rotateLog {

	logfile="$LOGDIR/$1"

	[[ -e $logfile.5.log ]] && rm $logfile.5.log
	[[ -e $logfile.4.log ]] && mv -f $logfile.4.log $logfile.5.log
	[[ -e $logfile.3.log ]] && mv -f $logfile.3.log $logfile.4.log
	[[ -e $logfile.2.log ]] && mv -f $logfile.2.log $logfile.3.log
	[[ -e $logfile.1.log ]] && mv -f $logfile.1.log $logfile.2.log
	[[ -e $logfile.log ]] && mv -f $logfile.log $logfile.1.log

	return 0
}

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

	return 0

}

function output {

	NOW=$(date +"%d-%m-%Y %T")
	[[ "$1" != '' ]] && COLOUR=$1 || COLOUR=$NC
	echo -e "$COLOUR$NOW ($SCRIPT_NAME)${@:2}${NC}"
	echo -e "$NOW ($SCRIPT_NAME)${@:2}" >> $LOGFILE

	return 0

}

function termColours {

	RED='\033[1;31m'
	YELLOW='\033[1;93m'
	NC='\033[0m' # No Color
	GREEN='\033[1;32m'
	PURPLE='\033[1;35m'
	BLUE='\033[1;34m'

	return 0

}
