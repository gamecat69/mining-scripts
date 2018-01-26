
import string

htmlTemplatePath = "html/index-template.html"

f = open(htmlTemplatePath)
data = f.read()
data = string.replace(data, '$minername', 'TBCTBCTBCTBC')
data = string.replace(data, '$lastupdate', 'TBCTBCTBCTBC')
data = string.replace(data, '$systemuptime', 'TBCTBCTBCTBC')
data = string.replace(data, '$avggputempC', 'TBCTBCTBCTBC')
data = string.replace(data, '$avggpufanspeed', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethusd', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethhashrate', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethshares', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethuptime', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethtotalshares', 'TBCTBCTBCTBC')
data = string.replace(data, '$ethpool', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmrusd', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmrhashrate', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmrshares', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmruptime', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmrtotalshares', 'TBCTBCTBCTBC')
data = string.replace(data, '$xmrpool', 'TBCTBCTBCTBC')
print (data)