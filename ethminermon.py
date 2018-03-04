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

url = "http://192.168.0.38:3333"
url = "http://localhost:3333"

def getEthminerData():

	#headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	data = {'id':'0','jsonrpc':'2.0','method':'miner_getstat1'}
	#data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
	#json_data = {"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}
	data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	res = requests.post(url, data=json.dumps(data), headers=headers)
	print (res.statuscode)
	#print (res.text)

getEthminerData()