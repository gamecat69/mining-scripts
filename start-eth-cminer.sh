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

SERVER1=`readJson config.json SERVER1`
SERVER2=`readJson config.json SERVER2`
ETHWALLET=`readJson config.json ETHWALLET`
WORKER=`readJson config.json MINERNAME`
EMAIL=`readJson config.json EMAIL`
POOLPASS=`readJson config.json POOLPASS`
CMINERDIR=`readJson config.json CMINERDIR`
LOGFILERETENTIONDAYS=`readJson config.json LOGFILERETENTIONDAYS`

#	Load variables from config file
#source ./config.sh

#SERVER1=eth-eu1.nanopool.org:9999
#SERVER2=eth-eu2.nanopool.org:9999
#ETHWALLET=0x75A3CdA475EE196916ec76C7174eCd7886163beC
#WORKER=gtx-1060x6-cminer
#EMAIL=nikansell00@gmail.com
#POOLPASS=x
#CMINERDIR="cminer9.4"
#CMINERDIR="cminer10.0"
#LOGFILERETENTIONDAYS=1

MININGCMD="./ethdcrminer64 -epool $SERVER1 -ewal $ETHWALLET.$WORKER/$EMAIL -epsw $POOLPASS -mode 1 -ftime 10 -ttli 80"

cd ~/$CMINERDIR

#   Delete files older than LOGFILERETENTIONDAYS
find $CMINERDIR/*_log.txt -mtime +$LOGFILERETENTIONDAYS -exec rm {} \;

#   Init epools.txt
echo "POOL: $SERVER1, WALLET: $ETHWALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" > epools.txt
echo "POOL: $SERVER2, WALLET: $ETHWALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" >> epools.txt 

echo $MININGCMD
$MININGCMD

