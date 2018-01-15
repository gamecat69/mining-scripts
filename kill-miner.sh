#!/bin/bash

echo "Killing miner"
pkill -f ethdcrminer64

echo "Killing NVIDIA logging"
pkill -f nvid-mon
