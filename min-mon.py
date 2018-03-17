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
#global xmrUSD
#global ethUSD

gpuDetails     = []
numGPU         = ''
avgGPUTemp     = ''
avgGPUFanSpeed = ''
avgGPUHashRate = ''

ethVersion    = ''
ethHashRate   = ''
ethPoolAddr   = ''
ethShares     = ''
ethUptime     = ''
ethSharePerHr = ''
ethMinerRestartTimestamp = 0

btcpVersion    = ''
btcpHashRate   = ''
btcpPoolAddr   = ''
btcpShares     = ''
btcpUptime     = ''
btcpSharePerHr = ''

btcpEarned     = 0.0
ethEarned      = 0.0
xmrEarned      = 0.0

xmrUSD        = ''
ethUSD        = ''
btcpUSD       = ''

xmrPoolAddr   = ''
xmrShares     = ''
xmrUptime     = ''
xmrSharePerHr = ''
xmrErrors     = ''
xmrVersion    = ''
xmrHashRate   = ''
xmrMinerRestartTimestamp = 0

#	----------------------------------
#	Functions
#	----------------------------------

def writeJSON():
	
	JSONfilepath = cfg["HTMLREPORTDIR"] + '/' + jsonReportFile
	print ("[MIN MON] Writing JSON report to: %s" % JSONfilepath)

	#data = {}
	#data['minername']=cfg["MINERNAME"]
	#data['lastupdate']=lastUpdate
	#data['systemuptime']=sysUptime
	#data['avggputemp']=str(avgGPUTemp)
	#data['avggpufanspeed']=str(avgGPUFanSpeed)
	#data['numGPU']=str(numGPU)
	#data['avggpuhashrate']=str(avgGPUHashRate)

	#data['ethhashrate']=str(ethHashRate)
	#data['ethshares']=str(ethShares)
	#data['ethuptime']=str(ethUptime)
	#data['ethtotalshares']=str(ethShares)
	#data['ethpool']=str(ethPoolAddr)

	#data['xmrhashrate']=str(xmrHashRate)
	#data['xmrshares']=str(xmrSharePerHr)
	#data['xmruptime']=str(xmrUptime)
	#data['xmrtotalshares']=str(xmrShares)
	#data['xmrpool']=str(xmrPoolAddr)

	#data['btcphashrate']=str(btcpHashRate)
	#data['btcpshares']=str(btcpSharePerHr)
	#data['btcpuptime']=str(btcpUptime)
	#data['btcptotalshares']=str(btcpShares)
	#data['btcppool']=str(btcpPoolAddr)

	#data['ethusd']=str(ethUSD)
	#data['xmrusd']=str(xmrUSD)
	#data['btcpusd']=str(btcpUSD)

	#data['ethEarned']=str(ethEarned)
	#data['btcpEarned']=str(btcpEarned)
	#data['xmrEarned']=str(xmrEarned)
	#data['ethMinerRestartTimestamp']=ethMinerRestartTimestamp

	print (json.dumps(data))

	try:
		JSONfile = open(JSONfilepath,"w")
		JSONfile.write(json.dumps(data))
		JSONfile.close()
	except Exception as e:
		logError("writeJSON: Unable to open JSON outputfile" + str(e))
		return "Error"

def getURL(url):

	try:
		res = requests.get(url, timeout=10)
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

	try:
		f = open(HTMLtemplatepath)
		data = f.read()
		f.close()
	except Exception as e:
		logError("writeHTML: Unable to open HTML template" + str(e))
		return "Error"
	
	data = string.replace(data, '$minername', str(data['minername']))
	data = string.replace(data, '$lastupdate', str(data['lastupdate']))
	data = string.replace(data, '$systemuptime', str(data['systemuptime']))
	data = string.replace(data, '$avggputemp', str(data['avggputemp']))
	data = string.replace(data, '$avggpufanspeed', str(data['avggpufanspeed']))

	data = string.replace(data, '$ethusd', str(data['ethusd']))
	data = string.replace(data, '$ethhashrate', str(data['ethhashrate']))
	data = string.replace(data, '$ethshares', str(data['ethsharesperhour']))
	data = string.replace(data, '$ethuptime', str(data['ethuptime']))
	data = string.replace(data, '$ethtotalshares', str(data['ethtotalshares']))
	data = string.replace(data, '$ethpool', str(data['ethpool']))

	data = string.replace(data, '$xmrusd', str(data['xmrusd']))
	data = string.replace(data, '$xmrhashrate', str(data['xmrhashrate']))
	data = string.replace(data, '$xmrshares', str(data['xmrsharesperhour']))
	data = string.replace(data, '$xmruptime', str(data['xmruptime']))
	data = string.replace(data, '$xmrtotalshares', str(data['xmrtotalshares']))
	data = string.replace(data, '$xmrpool', str(data['xmrpool']))
	data = string.replace(data, '$numGPU', str(data['numGPU']))
	data = string.replace(data, '$avggpuhashrate', str(data['avggpuhashrate']))

	data = string.replace(data, '$btcpusd', str(data['btcpusd']))
	data = string.replace(data, '$btcphashrate', str(data['btcphashrate']))
	data = string.replace(data, '$btcpshares', str(data['btcpshares']))
	data = string.replace(data, '$btcpuptime', str(data['btcpuptime']))
	data = string.replace(data, '$btcptotalshares', str(data['btcptotalshares']))
	data = string.replace(data, '$btcppool', str(data['btcppool']))
	
	data = string.replace(data, '$ethEarned', str(data['ethEarned']))
	data = string.replace(data, '$btcpEarned', str(data['btcpEarned']))
	data = string.replace(data, '$xmrEarned', str(data['xmrEarned']))

	try:
		HTMLfile = open(HTMLfilepath,"w")
		HTMLfile.write(data)
		HTMLfile.close()
	except Exception as e:
		logError("writeHTML: Unable to open HTML outputfile" + str(e))
		return "Error"

def unicodeToAscii(x):
    def unicode_to_str(x):
        return x.normalize("NFKD").encode("ascii", "ignore")

    return {unicode_to_str(k): unicode_to_str(v) for k, v in x.items()}

def getxmrStakData():

	#global xmrVersion
	#global xmrHashRate
	#global xmrPoolAddr
	#global xmrShares
	#global xmrUptime
	#global xmrSharePerHr
	#global xmrErrors
	#global xmrMinerRestartTimestamp

	print ("[MIN MON] Getting XMR data from: %s" % cfg["XMRSTAKURL"])

	try:
		data = getURL(cfg["XMRSTAKURL"])
	except:
		logError("getxmrStakData: Unable to open url. Restarting xmr-stak")
		xmrMinerRestartTimestamp = int(time.time())
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "xmr-stak problem, restarting..."])
		#subprocess.Popen(["./start-xmr.sh"])
		subprocess.Popen(["screen", "-dmS", "xmrstak", xmrMinerCmd])
		return "Error"
	
	xmrJson = json.loads(data)
	#xmrJson = unicodeToAscii(xmrJson)
	xmrJson=json.dumps(xmrJson)
	
	xmrShares     = int(xmrJson["results"]["shares_good"])
	
	#xmrVersion    = xmrJson["version"]
	#xmrHashRate   = int(xmrJson["hashrate"]["total"][0]) or 0
	#xmrPoolAddr   = xmrJson["connection"]["pool"]
	#xmrUptimeMin  = int(xmrJson["connection"]["uptime"] / 60)
	#xmrUptime     = formatUptimeMins(xmrJson["connection"]["uptime"] / 60)

	print ( type(xmrJson["connection"]["pool"]) )

	xmrtotalshares = xmrJson["results"]["shares_good"]
	xmrversion     = xmrJson["version"]
	xmrhashrate = int(xmrJson["hashrate"]["total"][0]) or 0
	xmrpool        = xmrJson["connection"]["pool"].encode('utf-8')
	xmruptimemins  = int(xmrJson["connection"]["uptime"] / 60)
	xmruptime      = formatUptimeMins(xmruptimemins)

	#	Prevent a divide by zero error
	if xmruptimemins > 0 and xmrShares > 0:
		xmrsharesperhour = "{0:.2f}".format(xmrtotalshares / ( xmruptimemins / 60 ))
	else:
		xmrsharesperhour = 0
	
	data['xmrtotalshares'] = str(xmrtotalshares)
	data['xmrhashrate'] = str(xmrhashrate)
	data['xmrversion'] = str(xmrversion)
	data['xmrpool'] = str(xmrpool)
	data['xmruptimemins'] = str(xmruptimemins)
	data['xmruptime'] = str(xmruptime)
	data['xmrsharesperhour'] = str(xmrsharesperhour)
	
	#xmrErrors     = xmrJson["connection"]["error_log"]
	data['xmrerrors'] = xmrJson["connection"]["error_log"]

def uploadToAWS(dir, file, prefix):

	#if prefix == '':
	#	prefix = '/'

	try:
		session=boto3.session.Session(
			region_name='eu-west-1',
			aws_access_key_id = cfg["ACCESSKEY"],
			aws_secret_access_key = cfg["SECRETKEY"],
		)
	except Exception as e:
		logError("uploadToAWS: Unable to create session" + str(e))
		return "Error"

	print ("[MIN MON] Uploading file: %s to bucket:%s/%s" % (dir + '/' + file, cfg["S3BUCKET"], prefix))
	
	try:
		s3client = session.client('s3', config= boto3.session.Config(signature_version='s3'))
		s3client.upload_file(dir + '/' + file, cfg["S3BUCKET"], prefix + file, ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})
	except Exception as e:
		logError("uploadToAWS: Unable to upload file" + str(e))
		return "Error"

def getEthminerData():

	# ['0.14.0.dev3', 
	#'59', ETH Shares
	#'120723;53;0', ETH Summary (hashrate;shares accepted;shares rejected)
	#'22272;19044;19044;22272;19044;19044', ETH Hasgrates
	#'0;0;0', DCR Summary (hashrate;shares accepted;shares rejected)
	#'off;off;off;off;off;off', DCR Hashrates
	#'64;37; 57;41; 58;43; 73;44; 62;47; 69;53', 
	#'http://eth1.nanopool.org:8888/0x75A3CdA475EE196916ec76C7174eCd7886163beC.gtx-1060x6-2-ethminer/nikansell00@gmail.com:', 
	#'0;0;0;0']

	host = "127.0.0.1"
	port = 3333

	gpuHashRates = []
	gpuTemps     = []
	gpuFanSpeeds = []

	global ethVersion
	#global ethHashRate
	#global ethPoolAddr
	#global ethShares
	#global ethUptime
	#global ethSharePerHr
	#global avgGPUTemp
	#global avgGPUFanSpeed
	#global numGPU
	#global avgGPUHashRate
	#global ethEarned
	global ethMinerRestartTimestamp

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
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
		ethMinerRestartTimestamp = int(time.time())
		print ("[MIN MON] ethMinerRestartTimestamp: %d" % (ethMinerRestartTimestamp))
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
	#numGPU = i
	data['numGPU']=i

	n=0
	while n < i:
		gpuTemps.append(gpu_temp_fanspeed[n*2])
		gpuFanSpeeds.append(gpu_temp_fanspeed[(n*2)+1])
		gpuDetails.append( gpuHashRates[n] + "," + gpuTemps[n] + "," + gpuFanSpeeds[n] )
		n=n+1

	ethVersion    = js["result"][0]
	#ethHashRate   = int(h_s_r[0])
	data['ethhashrate']=int(h_s_r[0])
	#ethPoolAddr   = js["result"][7]
	data['ethpool']= js["result"][7]
	#ethShares     = int(h_s_r[1])
	data['ethtotalshares']= int(h_s_r[1])
	#data['ethshares']=int(h_s_r[1])
	ethUptimeMin  = int(js["result"][1])
	#ethUptime     = formatUptimeMins(ethUptimeMin)
	data['ethuptime']=formatUptimeMins(ethUptimeMin)

	#	Extract just the pool address if its too long
	#	Ethminer provides a much longer URL than cminer
	if len(data['ethpool']) > 40:
		pattern="http://(.+?:\d+)/.+"
		m = re.match(pattern, data['ethpool'])
		if m:
			data['ethpool'] = m.group(1)

	#	Get average GPU temp
	tempTotal=0
	for t in gpuTemps:
		tempTotal = tempTotal + int(t)
	#avgGPUTemp = int(tempTotal / i)
	data['avggputemp']=int(tempTotal / i)

	#	Get average GPU fanspeed
	speedTotal=0
	for t in gpuFanSpeeds:
		speedTotal = speedTotal + int(t)
	#avgGPUFanSpeed = int(speedTotal / i)
	data['avggpufanspeed']=int(speedTotal / i)

	#	Get average GPU Hashrate
	#avgGPUHashRate = int(ethHashRate / i)
	data['avggpuhashrate']=int(data['ethhashrate'] / i)

	#	Prevent a divide by zero error
	#data['ethsharesperhour'] = 0.0
	if data['ethtotalshares'] > 0:
		data['ethsharesperhour'] = "{0:.2f}".format(data['ethtotalshares'] / ( ethUptimeMin / 60 ))
	else:
		data['ethsharesperhour'] = 0

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

	#global btcpVersion
	#global btcpHashRate
	#global btcpPoolAddr
	#global btcpShares
	#global btcpUptime
	#global btcpSharePerHr
	#global avgGPUTemp
	#global avgGPUFanSpeed
	#global numGPU
	#global avgGPUHashRate

	host = "127.0.0.1"
	port = 2222

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	print ("[MIN MON] Getting zminer data from: %s:%d" % (host, port))
	#print ("[MIN MON] getZminerData: Attemping to connect to %s:%d" % (host, port))
	try:
		s.connect((host, port))
		#print("[MIN MON] getZminerData: Connected, calling api")
		s.sendall('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n'.encode('utf-8'))
		#print("[MIN MON] getZminerData: Receiving data")
		j=s.recv(4096)
		#print("[MIN MON] getZminerData: Received %d bytes" % len(j) )
		#print("[MIN MON] getZminerData: Closing socket")
		s.close()
		js=json.loads(j.decode("utf-8"))
	except:
		logError("getZminerData: Unable to connect. Restarting zminer")
		subprocess.Popen(["./pushover.sh",cfg["MINERNAME"], "zminer problem, restarting..."])
		subprocess.Popen(["screen", "-dmS", "zminer", zMinerCmd])
		return "Error"

	#print("[MIN MON] getZminerData: Received data:\n%s" % js)

	result=js["result"]

	btcpVersion    = js["version"]
	btcpPoolAddr   = js["server"] + ':' + str(js["port"])
	btcpUptimeMin  = int(js["uptime"]) / 60
	btcpUptime     = formatUptimeMins(btcpUptimeMin)

	data['btcptotalshares']   = 0
	data['btcphashrate'] = 0

	i=0
	for gpu in result:
		gpuTemps.append(gpu["temperature"])
		gpuFanSpeeds.append("0") # not available
		data['btcphashrate'] = data['btcphashrate'] + int(gpu["avg_sol_ps"])
		data['btcptotalshares'] = data['btcptotalshares'] + int(gpu["accepted_shares"])
		i=i+1

	#numGPU = i
	data['numGPU']=i
	#avgGPUFanSpeed = 0 # Data not available
	data['avggpufanspeed']=0 # Data not available

	#	Get average GPU temp
	tempTotal=0
	for t in gpuTemps:
		tempTotal = tempTotal + int(t)
	
	#avgGPUTemp = int(tempTotal / i)
	data['avggputemp']=int(tempTotal / i)

	#	Get average GPU Hashrate
	#avgGPUHashRate = int(btcpHashRate / i)
	data['avggpuhashrate']=int(btcpHashRate / i)

	#	Prevent a divide by zero error
	if data['btcptotalshares'] > 0:
		data['btcpshares'] = "{0:.2f}".format(data['btcptotalshares'] / ( btcpUptimeMin / 60 ))
	else:
		data['btcpshares'] = 0

	#print("[MIN MON] btcpVersion: %s" % btcpVersion)
	#print("[MIN MON] btcpPoolAddr: %s" % btcpPoolAddr)
	#print("[MIN MON] btcpUptimeMin: %s" % btcpUptimeMin)
	#print("[MIN MON] btcpUptime: %s" % btcpUptime)
	#print("[MIN MON] gpuTemps: %s" % gpuTemps)
	#print("[MIN MON] gpuFanSpeeds: %s" % gpuFanSpeeds)
	#print("[MIN MON] btcpShares: %s" % btcpShares)
	#print("[MIN MON] avgGPUTemp: %s" % avgGPUTemp)
	#print("[MIN MON] avgGPUHashRate: %s" % avgGPUHashRate)
	#print("[MIN MON] btcpSharePerHr: %s" % btcpSharePerHr)

def getEarnedCoins():

	#global btcpEarned
	#global xmrEarned
	#global ethEarned

	#	Get Zminer (BTCP) info
	url = cfg["ZMINERSTATSURL"] + '?' + cfg["BTCPWALLET"]
	try:
		data = getURL(url)
		js=json.loads(data.decode("utf-8"))
		js = unicodeToAscii(js)
	except:
		logError("getEarnedCoins: Unable to get worker stats from url:%s" % url)
		return "Error"

	data['btcpEarned'] = js["balance"] + js["paid"]

	#	Get ETH balance
	#	https://eth.nanopool.org/api#api-Pool
	data['ethEarned'] = 0
	url = cfg["ETHMINERSTATSURL"] + '/balance/' + cfg["ETHWALLET"]
	try:
		data = getURL(url)
		js=json.loads(data.decode("utf-8"))
	except:
		logError("getEarnedCoins: Unable to get worker stats from url:%s" % url)
		return "Error"
	
	data['ethEarned'] = js["data"]
	
	#print("ETH Stats:%s" % js)

	#	Get ETH payments
	url = cfg["ETHMINERSTATSURL"] + '/payments/' + cfg["ETHWALLET"]
	try:
		data = getURL(url)
		js=json.loads(data.decode("utf-8"))
	except:
		logError("getEarnedCoins: Unable to get worker stats from url:%s" % url)
		return "Error"

	for payment in js["data"]:
		data['ethEarned'] = data['ethEarned'] + payment["amount"]

	#	Get XMR data
	#	http://api.minexmr.com:8080/stats_address?address=
	#	api code: https://github.com/zone117x/node-cryptonote-pool/blob/master/lib/api.js
	#	Other apis: live_stats, stats_address
	url = cfg["XMRMINERSTATSURL"] + cfg["XMRWALLET"]
	try:
		data = getURL(url)
		js=json.loads(data.decode("utf-8"))
		
	except:
		logError("getEarnedCoins: Unable to get worker stats from url:%s" % url)
		return "Error"

	xmrEarned = int(js["stats"]["balance"]) / 1000000000000

	for payment in js["payments"]:
		xmrEarned = xmrEarned + payment[1]
		#print("[MIN MON] xmrPayment: %s" % payment[1])
	
	data['ethEarned']  = "{0:.6f}".format(float(data['ethEarned']))
	data['btcpEarned'] = "{0:.6f}".format(float(data['btcpEarned']))
	data['xmrEarned']  = "{0:.6f}".format(float(data['xmrEarned']))

	#print("[MIN MON] ethEarned: %s" % ethEarned)
	#print("[MIN MON] btcpEarned: %s" % btcpEarned)
	#print("[MIN MON] xmrEarned: %s" % xmrEarned)

#	----------------------------------
#	Main code
#	----------------------------------

#	Initialize dict object to hold collected data
data = {}

#	Get config from json
cfg = json.load(open('config.json'))

#	Push miner name into the data dict
data['minername']=cfg["MINERNAME"]

miningRootDir  = "/home/mining/mining-scripts"
ethMinerCmd    = miningRootDir + "/" + "start-eth.sh"
xmrMinerCmd    = miningRootDir + "/" + "start-xmr.sh"
zMinerCmd      = miningRootDir + "/" + "start-zminer.sh"
htmlReportFile = cfg["MINERNAME"] + ".html"
jsonReportFile = cfg["MINERNAME"] + ".json"

#sysUptime      = getSystemUptime()
#lastUpdate     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
data['lastupdate'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
data['systemuptime'] = getSystemUptime()

if cfg["MINE_ETH"] == "yes":
	getEthminerData()

if cfg["MINE_XMR"] == "yes":
	getxmrStakData()

if cfg["MINE_BTCP"] == "yes":
	getZminerData()

getEarnedCoins()

data['xmrusd'] = getCoinUSD('monero')
data['ethusd'] = getCoinUSD('ethereum')
data['btcpusd'] = ''
writeHTML()
writeJSON()

#	Add a pause to try and stop occasional S3upload Bad Digest error
time.sleep(1)
uploadToAWS(cfg["HTMLREPORTDIR"], htmlReportFile, '')
uploadToAWS(cfg["HTMLREPORTDIR"], jsonReportFile, 'nodes/')
