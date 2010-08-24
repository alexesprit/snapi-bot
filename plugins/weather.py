# coding: utf-8;

# weather.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from xml.dom import minidom;

def showWeather(type, conference, nick, param):
	#try:
	query = urllib.urlencode({'q' : param.encode('cp1251')});
	text = urllib.urlopen(u'http://pda.rp5.ru/?lang=ru&%s' % (query)).read();
	if(text.count('1. <a href="')):
		idx = re.search('1. <a href="', text).end();
		text = text[idx:]
		idx = re.search('">', text).start();
		code = text[:idx];

		rawXml = minidom.parse(urllib.urlopen('http://rp5.ru/rss/%s' % (code)));
		message = '';
		for x in rawXml.getElementsByTagName('item'):
			title = x.getElementsByTagName('title')[0].firstChild.data.strip().split(': ', 1);
			desc = x.getElementsByTagName('description')[0].firstChild.data.strip();
			desc = desc.replace(', ', '\n');
			desc = desc.replace('%)', '%')
			desc = desc.replace(' (', ', ');
			desc = desc.replace(')', '');
			message += u'[%s]\nТемпература: %s\n\n' % (title[1], desc);
		message = u'Погода в городе %s\n%s' % (title[0], message);
		if(PUBLIC == type):
			sendMsg(type, conference, nick, u'скинула в личку');
		sendMsg(PRIVATE, conference, nick, message);
	else:
		sendMsg(type, conference, nick, u'не могу :(');

registerCommandHandler(showWeather, u'погода', 10, u'Показывает погоду', u'погода <город>', (u'погода Москва', ), ANY | PARAM);
