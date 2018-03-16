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

#XMR_WALLET=45kbjV6VRZ3GMPBHktLh9VGgun5nxEwtXS18yL8S23Gu8gvsE31JtMPHo6DwTwi4s4he3r6U5pmmo1ZhMVgsKrECPH3gBsk
#XMR_POOL=pool.minexmr.com:7777
#XMR_POOLPASS=x
#XMR_CPUONLY=yes
#XMR_CURRENCY=monero

if [ "$XMR_CPUONLY" = "yes" ] ; then

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMRPOOL -u $XMRWALLET -p $XMRPOOLPASS --currency  $XMRCURRENCY --noNVIDIA"   

else

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMRPOOL -u $XMRWALLET -p $XMRPOOLPASS --currency  $XMRCURRENCY" 

fi

output "Killing any previous xmr-stak process"
pkill -f xmr-stak

output $MININGCMD
$MININGCMD

