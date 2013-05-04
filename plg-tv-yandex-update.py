# coding: utf-8

import re

from module import io
from module import netutil

YANDEX_TV_URL = 'http://m.tv.yandex.ru/5'
TV_PROGRAM_FILE = 'tv-yandex.txt'

data = netutil.getURLResponseData(YANDEX_TV_URL, encoding='utf-8')
if data:
	channels = []
	entries = re.findall(r'<option value="(\d+)">(.+?)</option>', data)
	for entry in entries:
		number = int(entry[0])
		# 0-7 are categories numbers
		if number > 7:
			channel = entry[1].strip()
			channels.append((number, channel))
	out = open(TV_PROGRAM_FILE, 'wb')
	out.write('(\n')
	for ch in channels:
		number = ch[0]
		channel = ch[1].encode('utf-8')
		out.write("(%d, u'%s'), \n" % (number, channel))
	out.write(')\n')
	out.close()
