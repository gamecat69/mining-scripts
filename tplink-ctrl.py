import json
import requests
import time

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

def jsonPost(url, headers, json):

	try:
		print("jsonPost: Posting to: %s" % url)
		request = requests.post(url, headers=headers, json=json)
	except:
		print("jsonPost: Unable to connect")
		return 'error'

	return request.text

def processJson(data):
	#print("processJson: starting")

	try:
		js=json.loads(data)
	except:
		print("processJson: No valid JSON received")
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
	data = jsonPost(url, headers, jsonPostData)
	js = processJson(data)

	if not js:
		exit (1)
	else:
		print("powerCtrlTplinkDevice: Device powered %s" % powerStates[state])


def getTplinkDeviceInfo(deviceId):

	print("getTplinkDeviceInfo: Getting info from: %s" % deviceId)

	jsonPostData = {
		"method":"passthrough",
		"params":{
		"deviceId":deviceId,
		"requestData": "{\"system\":{\"get_sysinfo\":null},\"emeter\":{\"get_realtime\":null}}"
	 }
	}

	#print (json.dumps(jsonPostData))
	data = jsonPost(url, headers, jsonPostData)
	js = processJson(data)

	if not js:
		exit (1)
	
	#	OK. We have valid JSON
	errorcode = js['error_code']
	if errorcode == 0:
		print("getTplinkDeviceInfo: Post completed successfully")
	result = js['result']

	#	We got errorcode 0 from the server. Lets get the values we want.
	responseData = result['responseData']#['get_sysinfo']['relay_state']
	#print("responseData: %s" % responseData)

	#	Json does not fully decode, need to decode responseData
	js=json.loads(responseData.decode("utf-8"))
	sysInfo=js['system']['get_sysinfo']
	emeter=js['emeter']['get_realtime']
	powerState = sysInfo['relay_state']
	
	print("Device is powered %s" % powerStates[powerState])
	print("alias: %s" % sysInfo['alias'])
	print("on_time: %s" % formatUptimeMins(sysInfo['on_time']/60))
	print("latitude: %s" % sysInfo['latitude'])
	print("longitude: %s" % sysInfo['longitude'])

	print("power: %s Watts" % emeter['power'])
	print("current: %s amps" % emeter['current'])
	#print("total: %s" % emeter['total'])
	print("voltage: %s Volts" % emeter['voltage'])
	#print("err_code: %s" % emeter['err_code'])

def getTplinkDevices():

	jsonPostData = {"method":"getDeviceList"}
	
	#print (json.dumps(jsonPostData))
	data = jsonPost(url, headers, jsonPostData)
	js = processJson(data)

	if not js:
		exit (1)
	
	#	OK. We have valid JSON
	errorcode = js['error_code']
	if errorcode == 0:
		print("getTplinkDevices: Post completed successfully")
	
	result = js['result']

	#	We got errorcode 0 from the server. Lets get the values we want.
	for device in result['deviceList']:
		print("Device:")
		print("\tdeviceName: %s" % device['deviceName'])
		print("\tfwVer: %s" % device['fwVer'])
		print("\tstatus: %s" % device['status'])
		print("\talias: %s" % device['alias'])
		print("\tdeviceType: %s" % device['deviceType'])
		print("\tdeviceModel: %s" % device['deviceModel'])
		print("\tdeviceMac: %s" % device['deviceMac'])
		print("\tdeviceHwVer: %s" % device['deviceHwVer'])
		print("\tdeviceId: %s" % device['deviceId'])

cfg = json.load(open('config-tplink.json'))
host     = cfg['host']
deviceId = cfg['deviceId']
token    = cfg['token']

url         = host + "?token=" + token
headers     = {"Content-Type": "application/json"}
powerStates = ['off','on']

getTplinkDevices()
#getTplinkDeviceInfo(deviceId)

#powerCtrlTplinkDevice(deviceId,0)
#time.sleep(2)
#powerCtrlTplinkDevice(deviceId,1)


