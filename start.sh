#!/bin/bash

#	-------------------------------------
#	Function to get data from json file
#	-------------------------------------

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

MINERNAME=`readJson config.json MINERNAME`
PUSH_MSG=`readJson config.json PUSH_MSG`
MINMON_DELAY_SECS=`readJson config.json MINMON_DELAY_SECS`
MINE_XMR=`readJson config.json MINE_XMR`
MINE_ETH=`readJson config.json MINE_ETH`
ETHMINER=`readJson config.json ETHMINER`
S3BUCKET=`readJson config.json S3BUCKET`

S3URL = "http://$S3BUCKET.s3-website-eu-west-1.amazonaws.com/MINERNAME.html"
PUSH_MSG = "Starting up... Report URL: $S3URL"

#PUSH_MSG="Starting up...\
#Check here for report: http://min-mon.s3-website-eu-west-1.amazonaws.com"
#PUSH_TITLE="gtx-1060x6"

#	Get config data
#source ./config.sh

echo -e "${RED}Killing previous processes...${NC}"
./kill-miner.sh

echo -e "Starting wifi monitor"
./wifi-mon.sh &

echo "Configuring NVIDIA cards"
./nvidia-oc.sh

echo "Starting NVIDIA logging"
./nvidia-mon.sh &

if [ "$MINE_ETH" = "yes" ] ; then
    
    echo "Starting Ethminer"
    ./start-eth-ethminer.sh &

fi

if [ "$MINE_XMR" = "yes" ] ; then

   echo "Starting XMR Miner"
   ./start-xmr.sh &

fi

echo "Sending pushover message"
./pushover.sh "$MINERNAME" "$PUSH_MSG"

sleep $MINMON_DELAY_SECS

echo "Starting min-mon"
./min-mon.sh
