#!/bin/bash

#    Resets wifi adapter if connection drops

HOST_TO_PING="www.google.com"

while [ 1 = 1 ]
do

   if ping -c 1 $HOST_TO_PING >/dev/null 2>&1 ; then
      echo "[WIFI MON] Network up"
   else
      echo "[WIFI MON] Network down, resetting wifi card"
      nmcli radio wifi off
      nmcli radio wifi on
   fi

   sleep 60

do
