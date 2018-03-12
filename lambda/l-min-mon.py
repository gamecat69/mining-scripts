from __future__ import print_function
import os
import time
import datetime
import json
import boto3
from botocore.vendored import requests
import botocore

print('Loading function')

s3 = boto3.resource('s3')

USER   = os.environ['PUSHOVER_USER_ID']
API    = os.environ['PUSHOVER_API_TOKEN']
bucket = os.environ['BUCKET']
maxAge = int(os.environ['MAX_AGE'])

# miningRigs = {
# 	"gtx-1060x6-1" : 'gtx-1060x6-1.html',
# 	"gtx-1060x6-2" : 'gtx-1060x6-2.html'
# }

miningRigs = {
	"gtx-1060x6-1" : 'gtx-1060x6-1.html'
}

def send_message(text):
	payload = {"message": text, "user": USER, "token": API }
	r = requests.post('https://api.pushover.net/1/messages.json', data=payload, headers={'User-Agent': 'Python'})
	return r

def lambda_handler(event, context):
	
	try:

		for rig in miningRigs:
			print("Rig: %s" % rig)
			print("File: %s" % miningRigs[rig])
			key=miningRigs[rig]

			#	Get Last Modified date and time of file
			fileDetails=s3.ObjectSummary(bucket,key)
			fileDate=fileDetails.last_modified
		
			#	Convert fileDate to timestamp
			tsFileDate=fileDate.timestamp()
		
			#	Get the current timestamp and calculate the file age in seconds
			#	time.time() and datetime.datetime.timestamp() both return a float
			now = int(time.time())
			fileAgeSecs = now - int(tsFileDate)
			formatedTime=fileDate.strftime("%Y-%m-%d %H:%M:%S")
			#print("[%s] File is %d seconds old. Modified on: %s" % (rig, fileAgeSecs, formatedTime) )
		
			#	If file is older than maxAge, there is a problem...
			if fileAgeSecs > maxAge:
				print("Rig: %s is down" % (rig))
				send_message("Rig: %s is down" % (rig))
			else:
				print("Rig: %s is up" % (rig))

			# Read the hashrate from the file
			#fileObj  = s3.Object(bucket, key)
			#contents = fileObj.get()['Body'].read().decode('utf-8')
			#print(contents)

		return
	except Exception as e:
		print(e)
		print('Error getting details from object {} in bucket {}.'.format(key, bucket))
		raise e
		return 'error'
