#!/bin/bash

SCRIPT_NAME="KILLMINER"

function output {

	NOW=$(date +"%d-%m-%Y %T")
	echo -e "$NOW [$SCRIPT_NAME] $@"

}

output "Killing cminer"
pkill -f ethdcrminer64

output "Killing ethminer"
pkill -f ethminer

output "Killing NVIDIA logging"
pkill -f nvidia-mon

output "Killing xmr-stak"
pkill -f xmr-stak

output "Killing wifi-mon"
pkill -f wifi-mon

output "Killing min-mon"
pkill -f min-mon
