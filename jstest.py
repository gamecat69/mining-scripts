import json

# 	data = string.replace(data, '$minername', cfg["MINERNAME"])
# 	data = string.replace(data, '$lastupdate', lastUpdate)
# 	data = string.replace(data, '$systemuptime', sysUptime)
# 	data = string.replace(data, '$avggputemp', str(avgGPUTemp))
# 	data = string.replace(data, '$avggpufanspeed', str(avgGPUFanSpeed))
# 
# 	data = string.replace(data, '$ethusd', str(ethUSD))
# 	data = string.replace(data, '$ethhashrate', str(ethHashRate))
# 	data = string.replace(data, '$ethshares', str(ethSharePerHr))
# 	data = string.replace(data, '$ethuptime', str(ethUptime))
# 	data = string.replace(data, '$ethtotalshares', str(ethShares))
# 	data = string.replace(data, '$ethpool', str(ethPoolAddr))
# 
# 	data = string.replace(data, '$xmrusd', str(xmrUSD))
# 	data = string.replace(data, '$xmrhashrate', str(xmrHashRate))
# 	data = string.replace(data, '$xmrshares', str(xmrSharePerHr))
# 	data = string.replace(data, '$xmruptime', str(xmrUptime))
# 	data = string.replace(data, '$xmrtotalshares', str(xmrShares))
# 	data = string.replace(data, '$xmrpool', str(xmrPoolAddr))
# 	data = string.replace(data, '$numGPU', str(numGPU))
# 	data = string.replace(data, '$avggpuhashrate', str(avgGPUHashRate))
# 
# 	data = string.replace(data, '$btcpusd', str(btcpUSD))
# 	data = string.replace(data, '$btcphashrate', str(btcpHashRate))
# 	data = string.replace(data, '$btcpshares', str(btcpSharePerHr))
# 	data = string.replace(data, '$btcpuptime', str(btcpUptime))
# 	data = string.replace(data, '$btcptotalshares', str(btcpShares))
# 	data = string.replace(data, '$btcppool', str(btcpPoolAddr))
# 	
# 	data = string.replace(data, '$ethEarned', str(ethEarned))
# 	data = string.replace(data, '$btcpEarned', str(btcpEarned))
# 	data = string.replace(data, '$xmrEarned', str(xmrEarned))
# 


data = {}

data['minername']=cfg["MINERNAME"]
data['lastupdate']=lastUpdate
data['systemuptime']=sysUptime
data['avggputemp']=str(avgGPUTemp)
data['avggpufanspeed']=str(avgGPUFanSpeed)
data['numGPU']=str(numGPU)
data['avggpuhashrate']=str(avgGPUHashRate)

data['ethhashrate']=str(ethHashRate)
data['ethshares']=str(ethShares)
data['ethuptime']=str(ethUptime)
data['ethtotalshares']=str(ethShares)
data['ethpool']=str(ethPoolAddr)

data['xmrhashrate']=str(xmrHashRate)
data['xmrshares']=str(xmrSharePerHr)
data['xmruptime']=str(xmrUptime)
data['xmrtotalshares']=str(xmrShares)
data['xmrpool']=str(xmrPoolAddr)

data['btcphashrate']=str(btcpHashRate)
data['btcpshares']=str(btcpSharePerHr)
data['btcpuptime']=str(btcpUptime)
data['btcptotalshares']=str(btcpShares)
data['btcppool']=str(btcpPoolAddr)

data['ethusd']=str(ethUSD)
data['xmrusd']=str(xmrUSD)
data['btcpusd']=str(btcpUSD)

data['ethEarned']=str(ethEarned)
data['btcpEarned']=str(btcpEarned)
data['xmrEarned']=str(xmrEarned)

print (json.dumps(data))

