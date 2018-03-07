#!/bin/bash

SCRIPT_NAME="KILLMINER"

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
	echo -e "$NOW [$SCRIPT_NAME] $+"

}

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

WORKINGDIR=/home/mining/mining-scripts
cd $WORKINGDIR

PUSHOVER_USER=`readJson config.json PUSHOVER_USER`
PUSHOVER_TOKEN=`readJson config.json PUSHOVER_TOKEN`
CURLBIN=`readJson config.json CURLBIN`

TITLE=$(urlencode "$1")
MSG=$(urlencode "$2")
#CURLBIN=/usr/bin/curl

PUSHOVER_CMD="$CURLBIN -s \
-d user=$PUSHOVER_USER \
-d token=$PUSHOVER_TOKEN \
-d  message=$MSG \
-d title=$TITLE \
https://api.pushover.net/1/messages.json"

output "Running Pushover command:"
output $PUSHOVER_CMD
$PUSHOVER_CMD

