import json
#import urllib2
import re
import boto3
import datetime
import string
import os
import time
import requests
import subprocess
import socket

url = "http://192.168.0.38:3333"
url = "http://localhost:3333"
host = "192.168.0.38"
port = 3333

def formatUptimeMins(mins):
	
	mins = int(mins)

	# Helper vars:
	MINUTE  = 1
	HOUR    = 60
	DAY     = HOUR * 24

	# Get the days, hours, etc:
	days    = int( mins / DAY )
	hours   = int( ( mins % DAY ) / HOUR )
	minutes = int( ( mins % HOUR ) / MINUTE )

	# Build up the pretty string (like this: "N d N h N m")
	string = ""
	if days > 0:
		 string += str(days) + " d "
	if len(string) > 0 or hours > 0:
		 string += str(hours) + " h "
	if len(string) > 0 or minutes > 0:
		 string += str(minutes) + " m"
	else:
		string = "less than 1m"

	return string;

def logError(errString):
	print ("[MIN MON] [ERR] : %s" % errString)

def getEthminerData():

	# ['0.14.0.dev3', 
	#'59', 
	#'120723;53;0', 
	#'22272;19044;19044;22272;19044;19044', 
	#'0;0;0', 
	#'off;off;off;off;off;off', 
	#'64;37; 57;41; 58;43; 73;44; 62;47; 69;53', 
	#'http://eth1.nanopool.org:8888/0x75A3CdA475EE196916ec76C7174eCd7886163beC.gtx-1060x6-2-ethminer/nikansell00@gmail.com:', 
	#'0;0;0;0']

	gpuHashRates = []
	gpuTemps     = []
	gpuFanSpeeds = []

	global ethVersion
	global ethHashRate
	global ethPoolAddr
	global ethShares
	global ethUptime
	global ethSharePerHr
	global avgGPUTemp
	global avgGPUFanSpeed
	global numGPU
	global avgGPUHashRate

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print ("[MIN MON] getEthminerData: Attemping to connect to %s:%d" % (host, port))
	try:
		s.connect((host, port))
		print("[MIN MON] getEthminerData: Connected, calling jsonrpc api")
		s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		j=s.recv(2048)
		s.close()
		js=json.loads(j.decode("utf-8"))
		#resp=resp['result']
	except TimeoutError:
		logError("getEthminerData: Connection Timeout. Restarting ethminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "ethminer problem, restarting..."])
		subprocess.Popen(["./start-eth-ethminer.sh"])
		return "Error"
	except ConnectionRefusedError:
		logError("getEthminerData: Connection Timeout. Restarting ethminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "ethminer problem, restarting..."])
		subprocess.Popen(["./start-eth-ethminer.sh"])
		return "Error"
	except:
		logError("getEthminerData: Unable to connect. Restarting ethminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "ethminer problem, restarting..."])
		subprocess.Popen(["./start-eth-ethminer.sh"])
		return "Error"

	h_s_r=js["result"][2].split(';')
	gpu_hashrates=js["result"][3].split(';')
	gpu_temp_fanspeed=js["result"][6].split(';')
	pooladdr=js["result"][7]

	i=0
	for gpu in gpu_hashrates:
		gpuHashRates.append(gpu)
		i=i+1
	numGPU = i

	n=0
	while n < i:
		gpuTemps.append(gpu_temp_fanspeed[n*2])
		gpuFanSpeeds.append(gpu_temp_fanspeed[(n*2)+1])
		gpuDetails.append( gpuHashRates[n] + "," + gpuTemps[n] + "," + gpuFanSpeeds[n] )
		n=n+1

	ethVersion    = js["result"][0]
	ethHashRate   = int(h_s_r[0])
	ethPoolAddr   = js["result"][7]
	ethShares     = int(h_s_r[1])
	ethUptimeMin  = int(js["result"][1])
	ethUptime     = formatUptimeMins(ethUptimeMin)

	#	Get average GPU temp
	tempTotal=0
	for t in gpuTemps:
		print("temp:%s" % t)
		tempTotal = tempTotal + int(t)
	avgGPUTemp = tempTotal / i;

	#	Get average GPU fanspeed
	speedTotal=0
	for t in gpuFanSpeeds:
		speedTotal = speedTotal + int(t)
	avgGPUFanSpeed = speedTotal / i;

	#	Get average GPU Hashrate
	avgGPUHashRate = int(ethHashRate) / i

	#	Prevent a divide by zero error
	if ethShares > 0 and ethUptimeMin > 60:
		ethSharePerHr = ethShares // ( ethUptimeMin // 60 )
	else:
		ethSharePerHr = 0

	print (ethVersion)
	print (ethHashRate)
	print (ethPoolAddr)
	print (ethShares)
	print (ethUptimeMin)
	print (ethUptime)
	print (avgGPUTemp)
	print (avgGPUFanSpeed)
	print (avgGPUHashRate)
	print (ethSharePerHr)

getEthminerData()