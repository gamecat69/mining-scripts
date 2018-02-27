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

XMR_WALLET=`readJson config.json XMR_WALLET`
XMR_POOL=`readJson config.json XMR_POOL`
XMR_POOLPASS=`readJson config.json XMR_POOLPASS`
XMR_CPUONLY=`readJson config.json XMR_CPUONLY`
XMR_CURRENCY=`readJson config.json XMR_CURRENCY`

#XMR_WALLET=45kbjV6VRZ3GMPBHktLh9VGgun5nxEwtXS18yL8S23Gu8gvsE31JtMPHo6DwTwi4s4he3r6U5pmmo1ZhMVgsKrECPH3gBsk
#XMR_POOL=pool.minexmr.com:7777
#XMR_POOLPASS=x
#XMR_CPUONLY=yes
#XMR_CURRENCY=monero

if [ "$XMR_CPUONLY" = "yes" ] ; then

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMR_POOL -u $XMR_WALLET -p $XMR_POOLPASS --currency  $XMR_CURRENCY --noNVIDIA"   

else

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMR_POOL -u $XMR_WALLET -p $XMR_POOLPASS --currency  $XMR_CURRENCY" 

fi

echo $MININGCMD
$MININGCMD

