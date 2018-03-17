#!/bin/bash

SCRIPT_NAME="PUSHOVER"

#	Load common functions and paramaters
source ./bash-functions.sh
termColours
LOGFILE="$LOGDIR/$SCRIPT_NAME.log"

#	Rotate log
rotateLog $SCRIPT_NAME

urlencode() {
    # urlencode <string>

    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-:/]) printf "$c" ;;
            *) printf '%%%x' \'"$c" ;;
        esac
    done
}

#WORKINGDIR=/home/mining/mining-scripts
#cd $WORKINGDIR

PUSHOVER_USER=`readJson config.json PUSHOVER_USER`
PUSHOVER_TOKEN=`readJson config.json PUSHOVER_TOKEN`
CURLBIN=`readJson config.json CURLBIN`

TITLE=$(urlencode "$1")
MSG=$(urlencode "$2")

PUSHOVER_CMD="$CURLBIN -s \
-d user=$PUSHOVER_USER \
-d token=$PUSHOVER_TOKEN \
-d  message=$MSG \
-d title=$TITLE \
https://api.pushover.net/1/messages.json"

output "$BLUE" "[i] Running Pushover command:"
output "$GREEN" "[i] $PUSHOVER_CMD"
$PUSHOVER_CMD
output "$BLUE" "[i] ..."

