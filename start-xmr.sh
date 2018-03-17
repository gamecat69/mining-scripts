#!/bin/bash

SCRIPT_NAME="XMRMINER"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

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

output "$RED" "[i] Killing any previous xmr-stak process"
pkill -f xmr-stak

output "" "[i] $MININGCMD"
$MININGCMD

