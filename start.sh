#!/bin/bash

#	-------------------------------------
#	Function to get data from json file
#	-------------------------------------

SCRIPT_NAME="START"

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

MINERNAME=`readJson config.json MINERNAME`
MINE_XMR=`readJson config.json MINE_XMR`
MINE_ETH=`readJson config.json MINE_ETH`
MINE_BTCP=`readJson config.json MINE_BTCP`
ETHMINER=`readJson config.json ETHMINER`
S3BUCKET=`readJson config.json S3BUCKET`

S3URL="http://$S3BUCKET.s3-website-eu-west-1.amazonaws.com/$MINERNAME.html"
SCREEN_CMD="screen -dmS"
MYIP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
PUSH_MSG="[$MYIP] Starting up... Report URL: $S3URL"

output "${RED}Killing previous processes...${NC}"
./kill-miner.sh

output "Starting wifi monitor"
$SCREEN_CMD wifimon ./wifi-mon.sh &

#	All handled in /etc/rc.local now
#echo "Configuring NVIDIA cards"
#./nvidia-oc.sh

output "Starting NVIDIA logging"
./nvidia-mon.sh &

if [ "$MINE_ETH" = "yes" ] ; then
    
    output "Starting Ethminer"
    $SCREEN_CMD ethminer ./start-eth.sh &

fi

if [ "$MINE_XMR" = "yes" ] ; then

   output "Starting XMR Miner"
   $SCREEN_CMD xmrstak ./start-xmr.sh &

fi

if [ "$MINE_BTCP" = "yes" ] ; then

   output "Starting BTCP Miner"
   $SCREEN_CMD zminer ./start-zminer.sh &

fi

output "Sending pushover message"
./pushover.sh "$MINERNAME" "$PUSH_MSG"

#	Moved sleep logic into min-mon.sh
#sleep $MINMON_DELAY_SECS

output "Starting min-mon"
$SCREEN_CMD minmon ./min-mon.sh "boot" &
