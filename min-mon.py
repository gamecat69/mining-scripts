import json
import urllib2
import re
import boto3
import datetime
import string
import os

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
ethUptimeMin  = ''
ethSharePerHr = ''
xmrVersion    = ''
xmrHashRate   = ''
xmrPoolAddr   = ''
xmrShares     = ''
xmrUptimeMin  = ''
xmrSharePerHr = ''
xmrErrors     = ''
xmrUSD        = ''
ethUSD        = ''

#	----------------------------------
#	Functions
#	----------------------------------

def getCoinUSD(coin):

	url = cfg["COINMARKETCAPURL"] + '/' + coin

	print ("[MIN MON] Getting data from:%s" % url)

	res = urllib2.urlopen(url)
	data = res.read()
	Json = json.loads(data)
	return Json[0]["price_usd"]

def getSystemUptime():

     try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
     except:
        return "Cannot open uptime file: /proc/uptime"
 
     total_seconds = float(contents[0])
 
     # Helper vars:
     MINUTE  = 60
     HOUR    = MINUTE * 60
     DAY     = HOUR * 24
 
     # Get the days, hours, etc:
     days    = int( total_seconds / DAY )
     hours   = int( ( total_seconds % DAY ) / HOUR )
     minutes = int( ( total_seconds % HOUR ) / MINUTE )
     seconds = int( total_seconds % MINUTE )
 
     # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
     string = ""
     if days > 0:
         string += str(days) + " " + (days == 1 and "d" or "d" ) + " "
     if len(string) > 0 or hours > 0:
         string += str(hours) + " " + (hours == 1 and "h" or "h" ) + " "
     if len(string) > 0 or minutes > 0:
         string += str(minutes) + " " + (minutes == 1 and "m" or "m" ) + " "
     string += str(seconds) + " " + (seconds == 1 and "s" or "s" )
 
     return string;

def writeHTML():

	HTMLfilepath     = cfg["HTMLREPORTDIR"] + '/' + cfg["HTMLREPORTFILE"]
	HTMLtemplatepath = cfg["HTMLREPORTDIR"] + '/' + cfg["HTMLTEMPLATEFILE"]
	
	print ("[MIN MON] Writing HTML report to: %s" % HTMLfilepath)
	lastUpdate = datetime.datetime.now().strftime("%H:%M on %d-%m-%Y")
	sysUptime = getSystemUptime()

	f = open(HTMLtemplatepath)
	data = f.read()
	data = string.replace(data, '$minername', cfg["MINERNAME"])
	data = string.replace(data, '$lastupdate', lastUpdate)
	data = string.replace(data, '$systemuptime', sysUptime)
	data = string.replace(data, '$avggputemp', str(avgGPUTemp))
	data = string.replace(data, '$avggpufanspeed', str(avgGPUFanSpeed))
	data = string.replace(data, '$ethusd', str(ethUSD))
	data = string.replace(data, '$ethhashrate', str(ethHashRate))
	data = string.replace(data, '$ethshares', str(ethSharePerHr))
	data = string.replace(data, '$ethuptime', str(ethUptimeMin))
	data = string.replace(data, '$ethtotalshares', str(ethShares))
	data = string.replace(data, '$ethpool', str(ethPoolAddr))
	data = string.replace(data, '$xmrusd', str(xmrUSD))
	data = string.replace(data, '$xmrhashrate', str(xmrHashRate))
	data = string.replace(data, '$xmrshares', str(xmrSharePerHr))
	data = string.replace(data, '$xmruptime', str(xmrUptimeMin))
	data = string.replace(data, '$xmrtotalshares', str(xmrShares))
	data = string.replace(data, '$xmrpool', str(xmrPoolAddr))

	HTMLfile= open(HTMLfilepath,"w")
	HTMLfile.write(data)
	HTMLfile.close()

def getxmrStakData():

	global xmrVersion
	global xmrHashRate
	global xmrPoolAddr
	global xmrShares
	global xmrUptimeMin
	global xmrSharePerHr
	global xmrErrors

	print ("[MIN MON] Getting XMR data from:%s" % cfg["XMRSTAKURL"])

	res = urllib2.urlopen(cfg["XMRSTAKURL"])
	data = res.read()
	xmrJson = json.loads(data)
	
	xmrVersion    = xmrJson["version"]
	xmrHashRate   = xmrJson["hashrate"]["total"][0]
	xmrPoolAddr   = xmrJson["connection"]["pool"]
	xmrShares     = xmrJson["results"]["shares_good"]
	xmrUptimeMin  = xmrJson["connection"]["uptime"] / 60

	#	Prevent a divide by zero error
	if xmrShares > 0 and xmrUptimeMin > 60:
		xmrSharePerHr = xmrShares / (xmrUptimeMin / 60)
	else:
		xmrSharePerHr = 0
	xmrErrors     = xmrJson["connection"]["error_log"]
	
	#print ("xmrVersion:%s" % xmrVersion)
	#print ("xmrHashRate:%s h/s" % xmrHashRate)
	#print ("xmrPoolAddr:%s" % xmrPoolAddr)
	#print ("xmrShares:%s" % xmrShares) 
	#print ("xmrUptimeMin:%s" % xmrUptimeMin)
	#print ("xmrSharePerHr:%s" % xmrSharePerHr)
	#print ("xmrErrors:%s" % xmrErrors)

def uploadToAWS(dir, file):

	print ("[MIN MON] Logging into AWS")
	session=boto3.session.Session(
		region_name='eu-west-1',
		aws_access_key_id = cfg["ACCESSKEY"],
		aws_secret_access_key = cfg["SECRETKEY"],
	)

	print ("[MIN MON] Uploading file:%s to bucket:%s" % (dir + '/' + file, cfg["S3BUCKET"]))
	s3client = session.client('s3', config= boto3.session.Config(signature_version='s3'))
	s3client.upload_file(dir + '/' + file, cfg["S3BUCKET"], file, ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})

def getCminerData():

	gpuHashRates = []
	gpuTemps     = []
	gpuFanSpeeds = []

	global ethVersion
	global ethHashRate
	global ethPoolAddr
	global ethShares
	global ethUptimeMin
	global ethSharePerHr
	global avgGPUTemp
	global avgGPUFanSpeed

	#   Open cminer http interface and read

	print ("[MIN MON] Getting ETH data from:%s" % cfg["CMINERURL"])

	res = urllib2.urlopen(cfg["CMINERURL"])
	data = res.read()

	#   Split into a "lines" array
	#   The line we want is the second line

	lines = data.splitlines(True)
	#print lines[1]

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

		#print ("Version:%s" % js["result"][0])
		#print ("PoolAddr:%s" % js["result"][7])
		#print ("Uptime(mins):%s" % js["result"][1])
		#print ("Hashrate: %s Kh/s" % (h_s_r[0]))
		#print ("Shares_Accepted: %s" % (h_s_r[1]))
		#print ("Shares_Rejected: %s" % (h_s_r[2]))
		#print ("Avg Shares/hr:%s" % ( int(h_s_r[1]) / ( int(js["result"][1]) / 60 ) ) )

		i=0
		for gpu in gpu_hashrates:
		  #print ("GPU %d hashrate:%s" % (i, gpu))
		  gpuHashRates.append(gpu)
		  i=i+1

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
		  #print ("GPU %d temp:%s" % (n, gpu_temp_fanspeed[n*2]))
		  #print ("GPU %d fanspeed:%s" % (n, gpu_temp_fanspeed[(n*2)+1]))
		  gpuTemps.append(gpu_temp_fanspeed[n*2])
		  gpuFanSpeeds.append(gpu_temp_fanspeed[(n*2)+1])
		  gpuDetails.append( gpuHashRates[n] + "," + gpuTemps[n] + "," + gpuFanSpeeds[n] )
		  n=n+1

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

		ethVersion    = js["result"][0]
		ethHashRate   = h_s_r[0]
		ethPoolAddr   = js["result"][7]
		ethShares     = h_s_r[1]
		ethUptimeMin  = js["result"][1]

		#	Prevent a divide by zero error
		if ethShares > 0 and int(js["result"][1]) > 60:
			ethSharePerHr = int(h_s_r[1]) / ( int(js["result"][1]) / 60 )
		else:
			ethSharePerHr = 0

		#print ("ethVersion:%s" % ethVersion)
		#print ("ethHashRate:%s Kh/s" % ethHashRate)
		#print ("ethPoolAddr:%s" % ethPoolAddr)
		#print ("ethShares:%s" % ethShares) 
		#print ("ethUptimeMin:%s" % ethUptimeMin)
		#print ("ethSharePerHr:%s" % ethSharePerHr)
		#print ("avgGPUTemp:%s" % avgGPUTemp)
		
		#n=0
		#while n < i:
			#print ("GPU%d Info:%s" % (n, gpuDetails[n]) )
			#n=n+1

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
uploadToAWS(cfg["HTMLREPORTDIR"], cfg["HTMLREPORTFILE"])
