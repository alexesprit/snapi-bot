# coding: utf-8 

import re

from module import io
from module import netutil

S_TV_URL = 'http://s-tv.ru/old/tv/1tv/'
TV_PROGRAM_FILE = 'tvchannels.txt'

def getTVData():
	data = netutil.getURLResponseData(S_TV_URL, encoding='utf-8')
	if data:
		print len(data)
		# <a href="/old/tv/tv3/"><img src="http://img.s-tv.ru/logos/tv3.jpg" alt="ТВ-3" width="45px" title="ТВ-3" /></a>
		# <a href="/old/tv/ntv/"><img src="http://img.s-tv.ru/logos/ntv.jpg" alt="" /><span>НТВ</span></a>
		#elements = re.findall(r'<a href="(.+?)"><img.+?title="(.+?)" /></a>', data)
		elements = re.findall(r'<a href="(.+?)"><img src=.+?><span>(.+?)</span></a>', data)
		return elements
	return None
	
out = open(TV_PROGRAM_FILE, 'wb')
out.write('[\n')
for data in getTVData():
	chURL = data[0].encode('utf-8')
	chName = data[1].encode('utf-8')
	out.write('["%s", "%s"],\n' % (chName, chURL))
out.write(']\n')
out.close()
