import json

cfg = json.load(open('html/nodes.json'))

print(cfg['version'])
for rig in cfg['rigs']:
	if rig['monitor'] == 'yes':
		print(rig['name'])
		print(rig['deviceId'])
