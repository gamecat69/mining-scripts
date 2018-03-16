#!/bin/bash

SCRIPT_NAME="XMRMINER"

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

XMRWALLET=`readJson config.json XMRWALLET`
XMRPOOL=`readJson config.json XMRPOOL`
XMRPOOLPASS=`readJson config.json XMRPOOLPASS`
XMRCPUONLY=`readJson config.json XMRCPUONLY`
XMRCURRENCY=`readJson config.json XMRCURRENCY`

CONFDIR="$WORKINGDIR/conf/xmr-stak"
CPUFILE="$CONFDIR/cpu.txt"
NVIDIAFILE="$CONFDIR/nvidia.txt"
CFGFILE="$CONFDIR/config.txt"

CONFIG="--cpu $CPUFILE --nvidia $NVIDIAFILE -c $CFGFILE"
cd $CONFDIR

if [ "$XMRCPUONLY" = "yes" ] ; then

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMRPOOL -u $XMRWALLET -p $XMRPOOLPASS --currency $XMRCURRENCY $CONFIG --noNVIDIA"   

else

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMRPOOL -u $XMRWALLET -p $XMRPOOLPASS --currency $XMRCURRENCY $CONFIG" 

fi

output "Killing any previous xmr-stak process"
pkill -f xmr-stak

output $MININGCMD
$MININGCMD

