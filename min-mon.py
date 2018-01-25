import json
import urllib2
import re
import boto3
import datetime

#	----------------------------------
#	Pre-requisites
#	sudo apt-get install python-pip
#	pip install boto3
#	----------------------------------

global gpuDetails
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

#	----------------------------------
#	Functions
#	----------------------------------

def writeHTML():

	HTMLfilepath = cfg["HTMLREPORTDIR"] + '/' + cfg["HTMLREPORTFILE"]

	print ("[MIN MON] Writing HTML report to: %s" % HTMLfilepath)

	HTMLfile= open(HTMLfilepath,"w")
	HTMLfile.write("<!DOCTYPE html><html><body>\n")

	HTMLfile.write ("Last updated on: %s<br/>\n" % datetime.datetime.now() )

	HTMLfile.write ("xmrVersion: %s<br/>\n" % xmrVersion)
	HTMLfile.write ("xmrHashRate: %s h/s<br/>\n" % xmrHashRate)
	HTMLfile.write ("xmrPoolAddr: %s<br/>\n" % xmrPoolAddr)
	HTMLfile.write ("xmrShares: %s<br/>\n" % xmrShares) 
	HTMLfile.write ("xmrUptimeMin: %s<br/>\n" % xmrUptimeMin)
	HTMLfile.write ("xmrSharePerHr: %s<br/>\n" % xmrSharePerHr)
	HTMLfile.write ("xmrErrors: %s<br/>\n" % xmrErrors)

	HTMLfile.write ("ethVersion: %s<br/>\n" % ethVersion)
	HTMLfile.write ("ethHashRate: %s Kh/s<br/>\n" % ethHashRate)
	HTMLfile.write ("ethPoolAddr: %s<br/>\n" % ethPoolAddr)
	HTMLfile.write ("ethShares: %s<br/>\n" % ethShares) 
	HTMLfile.write ("ethUptimeMin: %s<br/>\n" % ethUptimeMin)
	HTMLfile.write ("ethSharePerHr: %s<br/>\n" % ethSharePerHr)

	HTMLfile.write("</body></html>")
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
	
	n=0
	while n < i:
		#print ("GPU%d Info:%s" % (n, gpuDetails[n]) )
		n=n+1

#	----------------------------------
#	Main code
#	----------------------------------

#	Get config from json
cfg = json.load(open('config.json'))

getCminerData()
getxmrStakData()
writeHTML()
uploadToAWS(cfg["HTMLREPORTDIR"], cfg["HTMLREPORTFILE"])
