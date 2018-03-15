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
minHashRate = int(os.environ['MIN_HASHRATE'])
host        = os.environ['TPLINK_HOST']
token       = os.environ['TPLINK_API_TOKEN']

tpLinkUrl   = host + "?token=" + token
headers     = {"Content-Type": "application/json"}
powerStates = ['off','on']


#	--------------------------------
#	To do

#	- Create checkFileAge()
#	- Create checkHashRate()
#	- Create updateError()
#	- Create powerCycleRig()
#	- Add DEBUG env var. Print out debug info if == 1
#	- Skip hashrate check if file is too old
#	- Create HTML report files using json in /nodes/<minername>-monitor.json
#	- Get CoinUSD values? - possible new Lambda
#	- Get current Coin balances? - possible new Lambda
#	--------------------------------

def updateConfig(data, key):

	client = boto3.client('s3')	

	try:	
		g = open('/tmp/' + key, 'w')
		g.write(json.dumps(data, indent=4, sort_keys=True))
		g.close()
	except:
		print("Failed to write file: %s" % '/tmp/' + key)
	
	try:
		with open('/tmp/' + key, 'rb') as f:
			client.upload_fileobj(f, bucket, key)
	except ClientError as e:
		print("Failed to upload file: %s" % e)	

def loadConfig():

	fileObj  = s3.Object(bucket, 'nodes.json')
	contents = fileObj.get()['Body'].read().decode('utf-8')
	#cfg      = json.loads(contents)
	return json.loads(contents)

def jsonPost(url, headers, json):

	try:
		print("jsonPost: Posting to: %s" % url)
		request = requests.post(url, headers=headers, json=json)
	except:
		print("jsonPost: Unable to connect")
		return 'error'

	return request.text

def processJson(data):
	print("processJson: starting")
	#print("Data:%s" % data)

	try:
		js=json.loads(data)
	#except ValueError as error:
	except:
		print("processJson: No valid JSON received. Error:%s" % error)
		return 'error'

	#	OK. We have valid JSON
	#print(js)
	errorcode = js['error_code']
	if errorcode == 0:
		print("processJson: Post completed successfully")
		return js
	else:
		print("processJson: Error: %s (%s)" % (errorcode, js['msg']))
		return ''

def powerCtrlTplinkDevice(deviceId, state):
	print("powerCtrlTplinkDevice: %s" % deviceId)
	print("Powering device: %s" % powerStates[state])

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
		print("powerCtrlTplinkDevice: Device powered %s" % powerStates[state])

def send_message(text):
	payload = {"message": text, "user": USER, "token": API }
	r = requests.post('https://api.pushover.net/1/messages.json', data=payload, headers={'User-Agent': 'Python'})
	return r

def lambda_handler(event, context):
	
	try:

		#	Load rig config from json
		cfg = loadConfig()
		
		#	Cycle through each rig in the json
		for rig in cfg['rigs']:

			#	Skip rig if not configured for monitoring
			if rig['monitor'] == 'no':
				break

			print("[%s] Checking rig..." % (rig['name']))

			key=rig['dataFile']        # json file with monitoring data
			minHashRate=rig['minKHs']  # min acceptable hashrate
			deviceId=rig['deviceId']   # TP-Link deviceId for power cyclcing
			lastError=rig['lastError'] # The previous error logged

			#	Get Last Modified date and time of monitoring data file
			fileDetails=s3.ObjectSummary(bucket,key)
			fileDate=fileDetails.last_modified
		
			#	Convert fileDate to timestamp
			tsFileDate=fileDate.timestamp()
		
			#	Get the current timestamp and calculate the file age in seconds
			#	time.time() and datetime.datetime.timestamp() both return a float
			now = int(time.time())
			fileAgeSecs = now - int(tsFileDate)
			formatedTime=fileDate.strftime("%Y-%m-%d %H:%M:%S")
			#print("[%s] File is %d seconds old. Modified on: %s" % (rig['name'], fileAgeSecs, formatedTime) )
		
			#	If file is older than maxAge, there is a problem...
			#	... the rig has not updated the file and  may be down.
			if fileAgeSecs > maxAge:

				if lastError == '':
					#	No previous error. Send message and update config file
					print("[%s] Rig is down. Will wait for one more failure before taking action" % (rig['name']))
					send_message("[%s] Rig is down. Will wait for one more failure before taking action" % (rig['name']))
					rig['lastError']="File not updated within time period"
					updateConfig(cfg, "nodes.json")
				else:
					#	Second failure. Take action
					send_message("[%s] Rig is down. Powercycling" % (rig['name']))
					powerCtrlTplinkDevice(deviceId,0)
					time.sleep(2)
					powerCtrlTplinkDevice(deviceId,1)
					
					#	Clear last error and update config file
					rig['lastError']=""
					updateConfig(cfg, "nodes.json")
			else:
				#	File has been updated recently. Clear error and update config file
				print("[%s] Rig is up" % (rig['name']))
				rig['lastError']=""
				updateConfig(cfg, "nodes.json")

			#	Read the hashrate from the file
			fileObj  = s3.Object(bucket, key)
			contents = fileObj.get()['Body'].read().decode('utf-8')
			js       = json.loads(contents)
			hashrate = int(js['ethhashrate'])
			print("[%s] Hashrate: %s" % (rig['name'], hashrate))
			
			#	Raise alert is hashrate too low
			if hashrate < minHashRate:
				
				if lastError == '':
					print("[%s] Hashrate Alert\nHashrate (%d) below threshold (%d).Will wait for one more failure before taking action" % (rig['name'], hashrate, minHashRate))
					send_message("[%s] Hashrate Alert\nHashrate (%d) below threshold (%d).Will wait for one more failure before taking action" % (rig['name'], hashrate, minHashRate))				
				else:
					print("[%s] Hashrate Alert\nHashrate (%d) below threshold (%d). Powercycling" % (rig['name'], hashrate, minHashRate))
					send_message("[%s] Hashrate Alert\nHashrate (%d) below threshold (%d). Powercycling" % (rig['name'], hashrate, minHashRate))
					powerCtrlTplinkDevice(deviceId,0)
					time.sleep(1)
					powerCtrlTplinkDevice(deviceId,1)
					rig['lastError']=""
					updateConfig(cfg, "nodes.json")
		return
	except Exception as e:
		print(e)
		print('Error getting details from object {} in bucket {}.'.format(key, bucket))
		raise e
		return 'error'
