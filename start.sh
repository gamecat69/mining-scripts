#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color
PUSH_MSG="Starting up...\
Check here for report: http://min-mon.s3-website-eu-west-1.amazonaws.com"
PUSH_TITLE="gtx-1060x6"
WAITSECS=20

WORKINGDIR=/home/mining/mining-scripts
cd $WORKINGDIR

#	Get config data
source ./config.sh

echo -e "${RED}Killing previous processes...${NC}"
./kill-miner.sh

echo -e "Starting wifi monitor"
./wifi-mon.sh &

echo "Configuring NVIDIA cards"
./nvidia-oc.sh

echo "Starting NVIDIA logging"
./nvidia-mon.sh &

if [ "$MINE_ETH" = "yes" ] ; then

   echo "Starting ETH Miner"
   ./start-eth-cminer.sh &

fi

if [ "$MINE_XMR" = "yes" ] ; then

   echo "Starting XMR Miner"
   ./start-xmr.sh &

fi

echo "Sending pushover message"
./pushover.sh "$PUSH_TITLE" "$PUSH_MSG"

sleep $WAITSECS

echo "Starting min-mon"
./min-mon.sh
