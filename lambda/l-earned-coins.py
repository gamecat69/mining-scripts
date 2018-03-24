from __future__ import print_function
import os
import time
import datetime
import json
import boto3
from botocore.vendored import requests
from botocore.exceptions import ClientError
import botocore

#s3 = boto3.resource('s3')

data={}
data['ethEarned'] = 0
data['btcpEarned'] = 0
data['xmrEarned'] = 0
data['xmrusd'] = 0
data['ethusd'] = 0
data['btcpusd'] = 0

debug = os.environ['DEBUG_MODE']

def getCoinUSD(coin):

	url = os.environ["COINMARKETCAPURL"] + '/' + coin
	#debugOutput("[i] Getting data from: %s" % url)
	js  = getJson(url)
	return js[0]["price_usd"]

def debugOutput(str):
	if debug == 'true':
		print(str)

def getJson(url):
	try:
		j = getURL(url)
		js=json.loads(j)
		return js
	except Exception as e:
		debugOutput("[e] getJson: Unable to get worker stats from url:%s (%s)" % (url, e))

def getURL(url):

	try:
		res = requests.get(url, timeout=10)
		return res.text
	except:
		debugOutput("[e] getURL: Unable to open url %s" % url)
		return "Error"
	
def jsonToS3File(data, bucket, key):

	#	AWS boto3 implementation does not support writing in-memory data to an S3 object
	#	... so we need to write to a tmp file then upload the tmp file
	client = boto3.client('s3')

	try:	
		g = open('/tmp/' + key, 'w')
		g.write(json.dumps(data, indent=4, sort_keys=True))
		g.close()
	except:
		debugOutput("[e] jsonToS3File: Failed to write file: %s" % '/tmp/' + key)
	
	try:
		with open('/tmp/' + key, 'rb') as f:
			client.upload_fileobj(f, bucket, key)
	except ClientError as e:
		debugOutput("[e] jsonToS3File: Failed to upload file: %s" % e)

def getEarnedCoins():

	#	Get Zminer (BTCP) info
	url = os.environ["ZMINERSTATSURL"] + '?' + os.environ["BTCPWALLET"]
	js  = getJson(url)
	
	data['btcpEarned'] = js["balance"] + js["paid"]

	#	Get ETH balance	
	url = os.environ["ETHMINERSTATSURL"] + '/balance/' + os.environ["ETHWALLET"]
	js  = getJson(url)
		
	data['ethEarned'] = js["data"]
	
	#	Get ETH payments
	url = os.environ["ETHMINERSTATSURL"] + '/payments/' + os.environ["ETHWALLET"]
	js  = getJson(url)

	if js["data"] != '':
		for payment in js["data"]:
			data['ethEarned'] = data['ethEarned'] + payment["amount"]

	#	Get XMR data
	#	http://api.minexmr.com:8080/stats_address?address=
	#	api code: https://github.com/zone117x/node-cryptonote-pool/blob/master/lib/api.js
	#	Other apis: live_stats, stats_address
	url = os.environ["XMRMINERSTATSURL"] + os.environ["XMRWALLET"]
	js  = getJson(url)

	data['xmrEarned'] = int(js["stats"]["balance"]) / 1000000000000

	for payment in js["payments"]:
		data['xmrEarned'] = data['xmrEarned'] + payment[1]
	
	data['ethEarned']  = round(data['ethEarned'], 6)
	data['btcpEarned'] = round(data['btcpEarned'], 6)
	data['xmrEarned']  = round(data['xmrEarned'], 6)

def lambda_handler(event, context):

    getEarnedCoins()
    data['xmrusd'] = getCoinUSD('monero')
    data['ethusd'] = getCoinUSD('ethereum')
    data['ethUsdValue']  = round(float(data['ethusd'])  * float(data['ethEarned']),3)
    data['xmrUsdValue']  = round(float(data['xmrusd'])  * float(data['xmrEarned']),3)
    data['btcpUsdValue'] = round(float(data['btcpusd']) * float(data['btcpEarned']),3)

    jsonToS3File(data, os.environ["S3_BUCKET"], 'earned-coins.json')
    return(data)
