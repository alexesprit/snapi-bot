# coding: utf-8 

import re

from module import io
from module import netutil

S_TV_URL = 'http://s-tv.ru/old/tv/1tv/'
TV_PROGRAM_FILE = 'tvchannels.txt'

def getTVData():
	data = netutil.getURLResponseData(S_TV_URL, encoding='utf-8')
	if data:
		elements = re.findall(r'<a href="(.+?)"><img src=.+?><span>(.+?)</span></a>', data)
		return elements
	return None
	
out = open(TV_PROGRAM_FILE, 'wb')
out.write('[\n')
for data in getTVData():
	chURL = data[0].encode('utf-8')
	if chURL[-1] == '/':
		chURL = chURL[:-1]
	chName = data[1].encode('utf-8').strip()
	out.write('[u"%s", "%s"],\n' % (chName, chURL))
out.write(']\n')
out.close()
