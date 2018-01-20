#!/bin/bash

MINE_XMR=yes
MINE_ETH=yes

echo "Killing previous processes..."
./kill-miner.sh

echo "Starting wifi monitor"
./wifi-mon.sh &

if [ "$MINE_ETH" = "yes" ] ; then

   echo "Starting ETH Miner"
   ./start-eth-cminer.sh &

fi

if [ "$MINE_XMR" = "yes" ] ; then

   echo "Starting XMR Miner"
   ./start-xmr.sh &

fi
