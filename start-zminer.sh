#!/bin/bash

SCRIPT_NAME="ZMINER"

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

export GPU_FORCE_64BIT_0=PTR
export GPU_MAX_HEAP_SIZE=100
export GPU_USE_SYNC_OBJECTS=1
export GPU_MAX_ALLOC_PERCENT=100
export GPU_SINGLE_ALLOC_PERCENT=100

BTCPSERVER=`readJson config.json BTCPSERVER`
BTCPSERVERPORT=`readJson config.json BTCPSERVERPORT`
BTCPWALLET=`readJson config.json BTCPWALLET`
WORKER=`readJson config.json MINERNAME`
EMAIL=`readJson config.json EMAIL`
POOLPASS=`readJson config.json POOLPASS`

output "Killing previous zminer process"
pkill -f "zm --server"
MININGCMD="/home/mining/zminer/zm --server $BTCPSERVER  --port $BTCPSERVERPORT --user $BTCPWALLET.$WORKER --telemetry --color"

output $MININGCMD
$MININGCMD
