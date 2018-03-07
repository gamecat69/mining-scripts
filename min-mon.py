from __future__ import division
import json
import urllib2
import re
import boto3
import datetime
import string
import os
import time
import requests
import subprocess
import socket

#	----------------------------------
#	Pre-requisites
#	sudo apt-get install python-pip
#	pip install boto3 requests
#	----------------------------------

global gpuDetails
global xmrUSD
global ethUSD

gpuDetails    = []
ethVersion    = ''
ethHashRate   = ''
ethPoolAddr   = ''
ethShares     = ''
ethUptime     = ''
ethSharePerHr = ''
xmrVersion    = ''
xmrHashRate   = ''
xmrPoolAddr   = ''
xmrShares     = ''
xmrUptime     = ''
xmrSharePerHr = ''
xmrErrors     = ''
xmrUSD        = ''
ethUSD        = ''
numGPU        = ''
avgGPUTemp    = ''
avgGPUTemp    = ''
avgGPUFanSpeed = ''
avgGPUHashRate = ''

#	----------------------------------
#	Functions
#	----------------------------------

def getURL(url):

	try:
		res = requests.get(url, timeout=5)
		return res.text
	except:
		logError("getURL: Unable to open url %s" % url)
		return "Error"

def logError(errString):
	print ("[MIN MON] [ERR] : %s" % errString)

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
	

def getCoinUSD(coin):

	url = cfg["COINMARKETCAPURL"] + '/' + coin

	print ("[MIN MON] Getting data from: %s" % url)

	try:
		data = getURL(url)
		Json = json.loads(data)
		return Json[0]["price_usd"]
	except Exception as e:
		logError("getCoinUSD: Unable to open url " + str(e))
		return "Error"

def getSystemUptime():

	try:
		f = open( "/proc/uptime" )
		contents = f.read().split()
		f.close()
	except Exception as e:
		logError("getSystemUptime: Unable to open /proc/uptime " + str(e))
		return "Error"

	total_seconds = float(contents[0])
	mins = int(total_seconds / 60)
	string = formatUptimeMins(mins)
	return string;

def writeHTML():

	HTMLfilepath     = cfg["HTMLREPORTDIR"] + '/' + htmlReportFile
	HTMLtemplatepath = cfg["HTMLREPORTDIR"] + '/' + cfg["HTMLTEMPLATEFILE"]
	
	print ("[MIN MON] Writing HTML report to: %s" % HTMLfilepath)
	lastUpdate = datetime.datetime.now().strftime("%H:%M on %d-%m-%Y")
	sysUptime = getSystemUptime()

	try:
		f = open(HTMLtemplatepath)
		data = f.read()
		f.close()
	except Exception as e:
		logError("writeHTML: Unable to open HTML template" + str(e))
		return "Error"
	
	data = string.replace(data, '$minername', cfg["MINERNAME"])
	data = string.replace(data, '$lastupdate', lastUpdate)
	data = string.replace(data, '$systemuptime', sysUptime)
	data = string.replace(data, '$avggputemp', str(avgGPUTemp))
	data = string.replace(data, '$avggpufanspeed', str(avgGPUFanSpeed))
	data = string.replace(data, '$ethusd', str(ethUSD))
	data = string.replace(data, '$ethhashrate', str(ethHashRate))
	data = string.replace(data, '$ethshares', str(ethSharePerHr))
	data = string.replace(data, '$ethuptime', str(ethUptime))
	data = string.replace(data, '$ethtotalshares', str(ethShares))
	data = string.replace(data, '$ethpool', str(ethPoolAddr))
	data = string.replace(data, '$xmrusd', str(xmrUSD))
	data = string.replace(data, '$xmrhashrate', str(xmrHashRate))
	data = string.replace(data, '$xmrshares', str(xmrSharePerHr))
	data = string.replace(data, '$xmruptime', str(xmrUptime))
	data = string.replace(data, '$xmrtotalshares', str(xmrShares))
	data = string.replace(data, '$xmrpool', str(xmrPoolAddr))
	data = string.replace(data, '$numGPU', str(numGPU))
	data = string.replace(data, '$avggpuhashrate', str(avgGPUHashRate))

	try:
		HTMLfile = open(HTMLfilepath,"w")
		HTMLfile.write(data)
		HTMLfile.close()
	except Exception as e:
		logError("writeHTML: Unable to open HTML outputfile" + str(e))
		return "Error"

def getxmrStakData():

	global xmrVersion
	global xmrHashRate
	global xmrPoolAddr
	global xmrShares
	global xmrUptime
	global xmrSharePerHr
	global xmrErrors

	print ("[MIN MON] Getting XMR data from: %s" % cfg["XMRSTAKURL"])

	try:
		data = getURL(cfg["XMRSTAKURL"])
		xmrJson = json.loads(data)
	except:
		logError("getxmrStakData: Unable to open url. Restarting xmr-stak")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "xmr-stak problem, restarting..."])
		#subprocess.Popen(["./start-xmr.sh"])
		subprocess.Popen(["screen", "-dmS", "xmrstak", xmrMinerCmd])
		return "Error"
	
	xmrVersion    = xmrJson["version"]
	xmrHashRate   = int(xmrJson["hashrate"]["total"][0])
	xmrPoolAddr   = xmrJson["connection"]["pool"]
	xmrShares     = int(xmrJson["results"]["shares_good"])
	xmrUptimeMin  = int(xmrJson["connection"]["uptime"] / 60)
	xmrUptime     = formatUptimeMins(xmrJson["connection"]["uptime"] / 60)

	#	Prevent a divide by zero error
	if xmrShares > 0:
		xmrSharePerHr = "{0:.2f}".format(xmrShares / ( xmrUptimeMin / 60 ))
	else:
		xmrSharePerHr = 0
	
	xmrErrors     = xmrJson["connection"]["error_log"]

def uploadToAWS(dir, file):

	try:
		session=boto3.session.Session(
			region_name='eu-west-1',
			aws_access_key_id = cfg["ACCESSKEY"],
			aws_secret_access_key = cfg["SECRETKEY"],
		)
	except Exception as e:
		logError("uploadToAWS: Unable to create session" + str(e))
		return "Error"

	print ("[MIN MON] Uploading file: %s to bucket:%s" % (dir + '/' + file, cfg["S3BUCKET"]))
	
	try:
		s3client = session.client('s3', config= boto3.session.Config(signature_version='s3'))
		s3client.upload_file(dir + '/' + file, cfg["S3BUCKET"], file, ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})
	except Exception as e:
		logError("uploadToAWS: Unable to upload file" + str(e))
		return "Error"

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

	host = "127.0.0.1"
	port = 3333

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
	print ("[MIN MON] Getting ETH data from: %s:%d" % (host, port))
	#print ("[MIN MON] getEthminerData: Attemping to connect to %s:%d" % (host, port))
	try:
		s.connect((host, port))
		#print("[MIN MON] getEthminerData: Connected, calling jsonrpc api")
		s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		j=s.recv(2048)
		s.close()
		js=json.loads(j.decode("utf-8"))
	except:
		logError("getEthminerData: Unable to connect. Restarting ethminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "ethminer problem, restarting..."])
		#subprocess.Popen(["./start-eth-ethminer.sh"])
		subprocess.Popen(["screen", "-dmS", "ethminer", ethMinerCmd])
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

	#	Extract just the pool address if its too long
	#	Ethminer provides a much longer URL than cminer
	if len(ethPoolAddr) > 40:
		pattern="http://(.+?:\d+)/.+"
		m = re.match(pattern, ethPoolAddr)
		if m:
			ethPoolAddr = m.group(1)

	#	Get average GPU temp
	tempTotal=0
	for t in gpuTemps:
		tempTotal = tempTotal + int(t)
	avgGPUTemp = int(tempTotal / i);

	#	Get average GPU fanspeed
	speedTotal=0
	for t in gpuFanSpeeds:
		speedTotal = speedTotal + int(t)
	avgGPUFanSpeed = int(speedTotal / i);

	#	Get average GPU Hashrate
	avgGPUHashRate = int(ethHashRate / i)

	#	Prevent a divide by zero error
	if ethShares > 0:
		ethSharePerHr = "{0:.2f}".format(ethShares / ( ethUptimeMin / 60 ))
	else:
		ethSharePerHr = 0

def getCminerData():

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

	#   Open cminer http interface and read

	print ("[MIN MON] Getting ETH data from: %s" % cfg["CMINERURL"])

	try:
		data = getURL(cfg["CMINERURL"])
	except:
		logError("getCminerData: Unable to open url. Restarting cminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "cminer problem, restarting..."])
		subprocess.Popen(["./start-eth-cminer.sh"])
		return "Error"

	#   Split into a "lines" array
	#   The line we want is the second line

	lines = data.splitlines(True)

	#   Remove everything after the '}'

	pattern="(^.+\}).*"
	m =re.match(pattern, lines[1])

	#   Pull out required data from the json
	#   Format:
	#   {"result": ["10.0 - ETH", "84", "99853;52;0", "20329;19891;19869;19884;19876", "0;0;0", "off;off;off;off;off", "56;42;65;39;67;40;67;40;56;36", "eth-eu1.nanopool.org:9999", "0;0;0;0"]}

	if m:

		#    Load the json object
		js = json.loads(m.group(1))

		h_s_r=js["result"][2].split(';')
		gpu_hashrates=js["result"][3].split(';')
		gpu_temp_fanspeed=js["result"][6].split(';')
		pooladdr=js["result"][7]

		i=0
		for gpu in gpu_hashrates:
		  gpuHashRates.append(gpu)
		  i=i+1

		numGPU = i

		#    Cycle through GPUs and get temp and fanspeed
		#    See below for data structure guidance
		#    GPU # = listindex, listindex 
		#    0 = 0,1
		#    1 = 2,3
		#    2 = 4,5
		#    3 = 6,7
		#    4 = 8,9

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

		#print ("[MIN MON] ETH Shares per hour calc. %d / (%d / 60)" % (ethShares, ethUptimeMin) )

def getZminerData():

	'''
	{
	   "id":1,
	   "result":[
		  {
			 "gpu_id":0,
			 "gpu_name":"GeForce GTX 1060 6GB",
			 "gpu_pci_bus_id":1,
			 "gpu_pci_device_id":0,
			 "gpu_uuid":"GPU-11ba3bf1-445f-bed4-7aef-6f18bae83c41",
			 "temperature":54,
			 "sol_ps":289.19,
			 "avg_sol_ps":288.87,
			 "sol_pw":3.36,
			 "avg_sol_pw":3.22,
			 "power_usage":85.96,
			 "avg_power_usage":89.70,
			 "accepted_shares":185,
			 "rejected_shares":0,
			 "latency":206
		  },
		  {
			...
		  }
	   ],
	   "uptime":29141,
	   "centime":29138,
	   "server":"eu.btcprivate.pro",
	   "port":2827,
	   "user":"b1GymVZkpvE5JGj1AbhDFwRMnADJkk4Cfw8.gtx-1060x6-2",
	   "version":"0.6",
	   "error":null
	}
	'''

	gpuHashRates = []
	gpuTemps     = []
	gpuFanSpeeds = []

	global btcpVersion
	global btcpHashRate
	global btcpPoolAddr
	global btcpShares
	global btcpUptime
	global btcpSharePerHr
	global avgGPUTemp
	global avgGPUFanSpeed
	global numGPU
	global avgGPUHashRate

	host = "127.0.0.1"
	port = 2222

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print ("[MIN MON] Getting zminer data from: %s:%d" % (host, port))
	print ("[MIN MON] getZminerData: Attemping to connect to %s:%d" % (host, port))
	try:
		s.connect((host, port))
		print("[MIN MON] getZminerData: Connected, calling api")
		#s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		print("[MIN MON] getZminerData: Receiving data")
		j=s.recv(4096)
		print("[MIN MON] getZminerData: Received %d bytes" % len(j) )
		print("[MIN MON] getZminerData: Closing socket")
		s.close()
		js=json.loads(j.decode("utf-8"))
	except:
		logError("getZminerData: Unable to connect. Restarting zminer")
		#subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "zminer problem, restarting..."])
		#subprocess.Popen(["screen", "-dmS", "zminer", zMinerCmd])
		return "Error"

	print("[MIN MON] getZminerData: Received data:\n%s" % js)

	result=js["result"]

	btcpVersion    = js["version"]
	btcpPoolAddr   = js["server"]
	btcpUptimeMin  = int(js["uptime"]) / 60
	btcpUptime     = formatUptimeMins(btcpUptimeMin)

	btcpShares   = 0

	for gpu in result:
		gpuTemps.append(gpu["temperature"])
		gpuFanSpeeds.append("0") # not available
		btcpShares = btcpShares + int(gpu["accepted_shares"])
	
	print("[MIN MON] btcpVersion: %s" % btcpVersion)
	print("[MIN MON] btcpPoolAddr: %s" % btcpPoolAddr)
	print("[MIN MON] btcpUptimeMin: %s" % btcpUptimeMin)
	print("[MIN MON] btcpUptime: %s" % btcpUptime)
	print("[MIN MON] gpuTemps: %s" % gpuTemps)
	print("[MIN MON] gpuFanSpeeds: %s" % gpuFanSpeeds)
	print("[MIN MON] btcpShares: %s" % btcpShares)

#	----------------------------------
#	Main code
#	----------------------------------

#	Get config from json
cfg = json.load(open('config.json'))

miningRootDir  = "/home/mining/mining-scripts"
ethMinerCmd    = miningRootDir + "/" + "start-eth.sh"
xmrMinerCmd    = miningRootDir + "/" + "start-xmr.sh"
zMinerCmd    = miningRootDir + "/" + "start-zminer.sh"
htmlReportFile = cfg["MINERNAME"] + ".html"

if cfg["MINE_ETH"] == "yes":
	#getCminerData()
	getEthminerData()

if cfg["MINE_XMR"] == "yes":
	getxmrStakData()

if cfg["MINE_BTCP"] == "yes":
	getZminerData()

xmrUSD = getCoinUSD('monero')
ethUSD = getCoinUSD('ethereum')
writeHTML()

#	Add a pause to try and stop occasional S3upload Bad Digest error
time.sleep(1)
uploadToAWS(cfg["HTMLREPORTDIR"], htmlReportFile)
