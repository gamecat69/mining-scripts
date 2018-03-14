#!/bin/bash

SCRIPT_NAME="ETHMINER"

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

SERVER1=`readJson config.json SERVER1`
SERVER2=`readJson config.json SERVER2`
ETHWALLET=`readJson config.json ETHWALLET`
WORKER=`readJson config.json MINERNAME`
EMAIL=`readJson config.json EMAIL`
POOLPASS=`readJson config.json POOLPASS`
CMINERDIR=`readJson config.json CMINERDIR`
LOGFILERETENTIONDAYS=`readJson config.json LOGFILERETENTIONDAYS`
PSERVER=`readJson config.json PSERVER`
FSERVER=`readJson config.json FSERVER`
ETHMINER=`readJson config.json ETHMINER`
MINE_DCR=`readJson config.json MINE_DCR`
DCRWALLET=`readJson config.json DCRWALLET`
DCRPOOL1=`readJson config.json DCRPOOL1`
DCRPOOL2=`readJson config.json DCRPOOL2`
DCRPOOL3=`readJson config.json DCRPOOL3`
DCRPOOL4=`readJson config.json DCRPOOL4`

export GPU_FORCE_64BIT_0=PTR
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

CMINERARGS=" -tt 68 -tstop 82 -dcri 10 -mport 3333 -ftime 10 -ttli 80"

output "Miner: $ETHMINER"

if [ "$ETHMINER" = "ethminer" ] ; then

    output "Killing previous ethminer process"
    pkill -f "ethminer --opencl"
    MININGCMD="/home/mining/ethminer/bin/ethminer --opencl -U -F $PSERVER/$ETHWALLET.$WORKER/$EMAIL --farm-recheck 200 --api-port 3333"

elif [ "$ETHMINER" = "cminer" ] ; then
	cd ~/$CMINERDIR
	output "Killing previous cminer process"
	pkill -f ethdcrminer64
	
	if [ "$MINE_DCR" = "yes" ]; then
	    output "Dual Mining (ETH + DCR)"
		MININGCMD="./ethdcrminer64 -epool $SERVER1 -ewal $ETHWALLET.$WORKER/$EMAIL -epsw $POOLPASS -dwal $DCRWALLET.$WORKER -dpool $DCRPOOL1 $CMINERARGS"

		#   Init dpools.txt
		echo "POOL: $DCRPOOL1, WALLET: $DCRWALLET.$WORKER, PSW: $POOLPASS" > dpools.txt
		echo "POOL: $DCRPOOL2, WALLET: $DCRWALLET.$WORKER, PSW: $POOLPASS" >> dpools.txt
		echo "POOL: $DCRPOOL3, WALLET: $DCRWALLET.$WORKER, PSW: $POOLPASS" >> dpools.txt
		echo "POOL: $DCRPOOL4, WALLET: $DCRWALLET.$WORKER, PSW: $POOLPASS" >> dpools.txt

	else
		MININGCMD="./ethdcrminer64 -epool $SERVER1 -ewal $ETHWALLET.$WORKER/$EMAIL -epsw $POOLPASS -mode 1 $CMINERARGS"	

		#   Init epools.txt
		echo "POOL: $SERVER1, WALLET: $ETHWALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" > epools.txt
		echo "POOL: $SERVER2, WALLET: $ETHWALLET.$WORKER/$EMAIL, WORKER: $WORKER, ESM: 0, ALLPOOLS: 0" >> epools.txt 

	fi
	#   Delete files older than LOGFILERETENTIONDAYS
	find ./*_log.txt -mtime +$LOGFILERETENTIONDAYS -exec rm {} \;

else
	output "[ERR] Unable to determing which ethminer to use"
fi
#   ------------------------
#   Start mining
#   ------------------------

output $MININGCMD
$MININGCMD

