#!/bin/bash

MINE_XMR=yes
MINE_ETH=yes
RED='\033[0;31m'
NC='\033[0m' # No Color
WORKINGDIR=/home/mining/mining-scripts
PUSH_MSG="Starting up...\
Check here for report: http://min-mon.s3-website-eu-west-1.amazonaws.com"
PUSH_TITLE="gtx-1060x5"
WAITSECS=20

cd $WORKINGDIR

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
