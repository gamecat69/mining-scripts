#!/bin/bash

#	-------------------------------------
#	Function to get data from json file
#	-------------------------------------

SCRIPT_NAME="START"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#LOGFILE="$WORKINGDIR/logs/start.log"

cd $WORKINGDIR

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

#	Create logdir if needed
mkdir -p "$WORKINGDIR/logs"

#	Init log file
echo -e "init" > $LOGFILE

output "$BLUE" "[i] Killing previous processes..."
./kill-miner.sh

output "$GREEN" "[i] Starting wifi monitor"
$SCREEN_CMD wifimon ./wifi-mon.sh &

#	All handled in /etc/rc.local now
#echo "Configuring NVIDIA cards"
#./nvidia-oc.sh

output "$GREEN" "[i] Starting NVIDIA logging"
./nvidia-mon.sh &

if [ "$MINE_ETH" = "yes" ] ; then
    
    output "$GREEN" "[i] Starting Ethminer"
    $SCREEN_CMD ethminer ./start-eth.sh &

fi

if [ "$MINE_XMR" = "yes" ] ; then

   output "$GREEN" "[i] Starting XMR Miner"
   $SCREEN_CMD xmrstak ./start-xmr.sh &

fi

if [ "$MINE_BTCP" = "yes" ] ; then

   output "$GREEN" "[i] Starting BTCP Miner"
   $SCREEN_CMD zminer ./start-zminer.sh &

fi

output "$GREEN" "[i] Sending pushover message"
./pushover.sh "$MINERNAME" "$PUSH_MSG"

#	Moved sleep logic into min-mon.sh
#sleep $MINMON_DELAY_SECS

output "$GREEN" "[i] Starting min-mon"
$SCREEN_CMD minmon ./min-mon.sh "boot" &
