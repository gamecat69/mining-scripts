#!/bin/bash

#    Resets wifi adapter if connection drops

HOST_TO_PING="www.google.com"
RED='\033[0;31m'
NC='\033[0m' # No Color

while [ 1 = 1 ]
do

   if ping -c 1 $HOST_TO_PING >/dev/null 2>&1 ; then
      echo -e "${NC}[WIFI MON] Network up"
   else
      echo -e "${RED}[WIFI MON] Network down, resetting wifi card${NC}"
      nmcli radio wifi off
      nmcli radio wifi on
   fi

   sleep 60

done
