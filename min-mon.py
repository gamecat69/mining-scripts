import json
import urllib2
import re
import boto3
import datetime
import string
import os
import time

#	----------------------------------
#	Pre-requisites
#	sudo apt-get install python-pip
#	pip install boto3
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
		res = urllib2.urlopen(url)
		data = res.read()
		Json = json.loads(data)
		#print ("[MIN MON]    Got: %s" % Json[0]["price_usd"])
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

	HTMLfilepath     = cfg["HTMLREPORTDIR"] + '/' + cfg["HTMLREPORTFILE"]
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
		res = urllib2.urlopen(cfg["XMRSTAKURL"])
		data = res.read()
		xmrJson = json.loads(data)
	except Exception as e:
		logError("getxmrStakData: Unable to open url" + str(e))
		return "Error"
	
	xmrVersion    = xmrJson["version"]
	xmrHashRate   = int(xmrJson["hashrate"]["total"][0])
	xmrPoolAddr   = xmrJson["connection"]["pool"]
	xmrShares     = int(xmrJson["results"]["shares_good"])
	xmrUptimeMin  = int(xmrJson["connection"]["uptime"] / 60)
	xmrUptime     = formatUptimeMins(xmrJson["connection"]["uptime"] / 60)

	#	Prevent a divide by zero error
	if xmrShares > 0 and xmrUptimeMin > 60:
		xmrSharePerHr = xmrShares / (xmrUptimeMin / 60)
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
		res = urllib2.urlopen(cfg["CMINERURL"])
		data = res.read()
	except Exception as e:
		logError("getCminerData: Unable to open url" + str(e))
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

#	----------------------------------
#	Main code
#	----------------------------------

#	Get config from json
cfg = json.load(open('config.json'))

getCminerData()
getxmrStakData()
xmrUSD = getCoinUSD('monero')
ethUSD = getCoinUSD('ethereum')
writeHTML()
#	Add a pause to try and stop occasional S3upload Bad Digest error
time.sleep(1)
uploadToAWS(cfg["HTMLREPORTDIR"], cfg["HTMLREPORTFILE"])