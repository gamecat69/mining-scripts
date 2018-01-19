#!/bin/bash

XMR_WALLET=45kbjV6VRZ3GMPBHktLh9VGgun5nxEwtXS18yL8S23Gu8gvsE31JtMPHo6DwTwi4s4he3r6U5pmmo1ZhMVgsKrECPH3gBsk
XMR_POOL=pool.minexmr.com:7777
XMR_POOLPASS=x
XMR_CPUONLY=yes
XMR_CURRENCY=monero

if [ "$XMR_CPUONLY" = "yes" ] ; then

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMR_POOL -u $XMR_WALLET -p $XMR_POOLPASS --currency  $XMR_CURRENCY --noNVIDIA"   

else

   MININGCMD="/home/mining/xmr-stak/bin/xmr-stak -o $XMR_POOL -u $XMR_WALLET -p $XMR_POOLPASS --currency  $XMR_CURRENCY" 

fi

echo $MININGCMD
$MININGCMD

