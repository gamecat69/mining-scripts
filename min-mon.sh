#!/bin/bash

WAITSECS=300
YELLOW='\033[0;93m'
NC='\033[0m' # No Color

#	Call the python script in a loop

while [ 1 = 1 ]
do

   echo -e "${YELLOW}[MIN MON] Getting Mining Stats"
   python min-mon.py
   echo -e "${YELLOW}[MIN MON] Sleeping for $WAITSECS${NC}"
   sleep $WAITSECS

done
