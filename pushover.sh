#!/bin/bash


WORKINGDIR=/home/mining/mining-scripts

cd $WORKINGDIR

#   Get TOKEN and USER from config.sh
source ./config.sh

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

TITLE=$(urlencode "$1")
MSG=$(urlencode "$2")
CURLBIN=/usr/bin/curl

PUSHOVER_CMD="$CURLBIN -s \
-d user=$PUSHOVER_USER \
-d token=$PUSHOVER_TOKEN \
-d  message=$MSG \
-d title=$TITLE \
https://api.pushover.net/1/messages.json"

echo "Running Pushover command:"
echo $PUSHOVER_CMD
$PUSHOVER_CMD

