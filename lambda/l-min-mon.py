from __future__ import print_function
import os
import time
import datetime
import json
import boto3
from botocore.vendored import requests
from botocore.exceptions import ClientError
import botocore

print('Loading function')

s3 = boto3.resource('s3')

USER        = os.environ['PUSHOVER_USER_ID']
API         = os.environ['PUSHOVER_API_TOKEN']
bucket      = os.environ['BUCKET']
maxAge      = int(os.environ['MAX_AGE'])
host        = os.environ['TPLINK_HOST']
token       = os.environ['TPLINK_API_TOKEN']
testMode    = os.environ['TEST_MODE']
debug       = os.environ['DEBUG_MODE']

tpLinkUrl   = host + "?token=" + token
headers     = {"Content-Type": "application/json"}
powerStates = ['off','on']

#	--------------------------------
#	To do

#	- Create HTML report files using json in /nodes/<minername>-monitor.json
#	- Get CoinUSD values? - possible new Lambda
#	- Get current Coin balances? - possible new Lambda
#	--------------------------------

def debugOutput(str):
	if debug == 'true':
		print(str)

def powerCycleRig(deviceId):
	powerCtrlTplinkDevice(deviceId,0)
	time.sleep(1)
	powerCtrlTplinkDevice(deviceId,1)

def getS3JsonData(bucket, key, param):

	try:
		fileObj  = s3.Object(bucket, key)
		contents = fileObj.get()['Body'].read().decode('utf-8')
	except:
		sendMessage("getS3JsonData: Cannot get object S3://%s/%s." % (bucket,key))
		return False

	try:
		js    = json.loads(contents)
		value = int(js[param])
	except:
		sendMessage("getS3JsonData: Cannot get %s from object S3://%s/%s." % (param,bucket,key))
		return False

	return value

def getS3FileAge(bucket, key):

	try:
		#	Get Last Modified date and time of monitoring data file
		fileDetails=s3.ObjectSummary(bucket,key)
	except:
		sendMessage("getS3FileAge: Cannot get age for object S3://%s/%s" % (bucket,key))
		return False

	#	Get fileData and convert to timestamp
	fileDate=fileDetails.last_modified
	tsFileDate=fileDate.timestamp()

	#	Get the current timestamp and calculate the file age in seconds
	#	time.time() and datetime.datetime.timestamp() both return a float
	now = int(time.time())
	fileAgeSecs = now - int(tsFileDate)

	#formatedTime=fileDate.strftime("%Y-%m-%d %H:%M:%S")
	#debugOutput("[%s] File is %d seconds old. Modified on: %s" % (rig['name'], fileAgeSecs, formatedTime) )

	return fileAgeSecs

def jsonToS3File(data, key):

	#	AWS boto3 implementation does not support writing in-memory data to an S3 object
	#	... so we need to write to a tmp file then upload the tmp file
	client = boto3.client('s3')

	try:	
		g = open('/tmp/' + key, 'w')
		g.write(json.dumps(data, indent=4, sort_keys=True))
		g.close()
	except:
		debugOutput("Failed to write file: %s" % '/tmp/' + key)
	
	try:
		with open('/tmp/' + key, 'rb') as f:
			client.upload_fileobj(f, bucket, key)
	except ClientError as e:
		debugOutput("Failed to upload file: %s" % e)	

def loadConfig():

	fileObj  = s3.Object(bucket, 'nodes.json')
	contents = fileObj.get()['Body'].read().decode('utf-8')
	#cfg      = json.loads(contents)
	return json.loads(contents)

def jsonPost(url, headers, json):

	try:
		debugOutput("jsonPost: Posting to: %s" % url)
		request = requests.post(url, headers=headers, json=json)
	except:
		debugOutput("jsonPost: Unable to connect")
		return 'error'

	return request.text

def processJson(data):
	#debugOutput("processJson: starting")
	#print("Data:%s" % data)

	try:
		js=json.loads(data)
	#except ValueError as error:
	except:
		debugOutput("processJson: No valid JSON received. Error:%s" % error)
		return 'error'

	#	OK. We have valid JSON
	#print(js)
	errorcode = js['error_code']
	if errorcode == 0:
		debugOutput("processJson: Post completed successfully")
		return js
	else:
		debugOutput("processJson: Error: %s (%s)" % (errorcode, js['msg']))
		return ''

def powerCtrlTplinkDevice(deviceId, state):
	
	debugOutput("powerCtrlTplinkDevice: %s" % deviceId)
	debugOutput("Powering device: %s" % powerStates[state])

	jsonPostData = {
		"method":"passthrough",
		"params":{
		"deviceId":deviceId,
		"requestData":"{\"system\":{\"set_relay_state\":{\"state\":" + str(state) + "}}}"
	 }
	}

	#print (json.dumps(jsonPostData))
	data = jsonPost(tpLinkUrl, headers, jsonPostData)
	js = processJson(data)

	if not js:
		exit (1)
	else:
		debugOutput("powerCtrlTplinkDevice: Device powered %s" % powerStates[state])

def sendMessage(text):

	debugOutput("Sending message: %s" % (text) )
	
	if testMode != 'true':
		payload = {"message": text, "user": USER, "token": API }
		r = requests.post('https://api.pushover.net/1/messages.json', data=payload, headers={'User-Agent': 'Python'})
		return r

def lambda_handler(event, context):
	
	try:
		#	Load rig config from json
		cfg = loadConfig()

	except Exception as e:
		#	Failed to load config from json
		debugOutput(e)
		debugOutput('Unable to load config from s3://%s/%s' % (bucket, key))
		raise e
		return 'error'
		
	#	We have data. Cycle through each rig in the json
	for rig in cfg['rigs']:

		#	Skip rig if not configured for monitoring
		if rig['monitor'] == 'no':
			break

		print("[%s] Checking rig..." % (rig['name']))

		dataFile    = rig['dataFile']  # json file with monitoring data
		minHashRate = rig['minKHs']    # min acceptable hashrate
		deviceId    = rig['deviceId']  # TP-Link deviceId for power cyclcing
		lastError   = rig['lastError'] # The previous error logged
		bootTimestamp = rig['bootTimestamp'] # When the rig was last powercycled

		if bootTimestamp != '':
			#	This server was powercycled recently. Make sure it has 3mins to boot
			now = int(time.time())
			uptimeSecs = now - int(bootTimestamp)
			debugOutput("[%s] Server Uptime: %d secs" % (rig['name'], uptimeSecs))
			
			if uptimeSecs < 180:
				#	Server powercycled in less than 3 mins, skip
				print("[%s] Rig powercycled %d secs ago. Skipping" % (rig['name'], uptimeSecs))
				break

		#	Find out when the data file was last updated
		fileAgeSecs = getS3FileAge(bucket, dataFile) or 0
		debugOutput("[%s] Last update was %d secs ago" % (rig['name'], fileAgeSecs))
	
		#	If file is older than maxAge, there is a problem...
		#	... the rig has not updated the file and may be down.
		if fileAgeSecs > maxAge:
			
			if testMode == 'true':
				debugOutput("[%s] (Test Mode) Rig is down. Powercycling" % (rig['name']))
			else:
				sendMessage("[%s] Rig is down. Powercycling" % (rig['name']))
				powerCycleRig(deviceId)
			
			#	Update json dataFile
			rig['lastError']="powercycle"
			debugOutput("[%s] Updating bootTimestamp to %d" % (rig['name'], int(time.time())))
			rig['bootTimestamp']=int(time.time())
			jsonToS3File(cfg, "nodes.json")

		else:

			#	File has been updated recently. Check the hashrate
			print("[%s] Rig is up. Checking hashrate" % (rig['name']))

			#	Read values from dataFile
			hashrate = getS3JsonData(bucket, dataFile, 'ethhashrate') or 0
			ethMinerRestartTimestamp = getS3JsonData(bucket, dataFile, 'ethMinerRestartTimestamp') or 0
			print("[%s] Hashrate: %s" % (rig['name'], hashrate))
			debugOutput("[%s] ethMinerRestartTimestamp: %d" % (rig['name'], ethMinerRestartTimestamp))
			
			#	Find out when the eth miner was last restarted
			now = int(time.time())
			print("[%s] Current timestamp: %d" % (rig['name'], now))
			ethMinerUptimeSecs = now - int(ethMinerRestartTimestamp)
			
			if ethMinerUptimeSecs < 80 and ethMinerUptimeSecs > 0:
				#	Eth Miner restarted less than 60 secs ago, skip
				print("[%s] Eth Miner restarted %d secs ago. Skipping" % (rig['name'], ethMinerUptimeSecs))
				break
		
			if hashrate < minHashRate:
			
				#	Raise alert. Hashrate too low
				sendMessage("[%s] Hashrate Alert\nHashrate (%d) below threshold (%d). Powercycling" % (rig['name'], hashrate, minHashRate))
				
				if testMode == 'true':			
					debugOutput("[%s] (Test Mode) Hashrate Alert. Powercycling" % (rig['name']))
				else:	
					powerCycleRig(deviceId)

				#	Add error to data file
				rig['lastError']="hashrate"
				debugOutput("[%s] Updating bootTimestamp to %d" % (rig['name'], int(time.time())))
				rig['bootTimestamp']=int(time.time())
				jsonToS3File(cfg, "nodes.json")
			else:
				#	Update last error in data file
				rig['lastError']=""
				jsonToS3File(cfg, "nodes.json")					

	#	All rigs processes. quit function
	return
