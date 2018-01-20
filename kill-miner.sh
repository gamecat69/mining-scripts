#!/bin/bash

echo "Killing cminer"
pkill -f ethdcrminer64

echo "Killing ethminer"
pkill -f ethminer

echo "Killing NVIDIA logging"
pkill -f nvid-mon

echo "Killing xmr-stak"
pkill -f xmr-stak

echo "Killing wifi-mon"
pkill -f wifi-mon
