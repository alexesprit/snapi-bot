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

def showWeather(msgType, conference, nick, param):
	query = urllib.urlencode({'q' : param.encode('cp1251')});
	text = urllib.urlopen(u'http://pda.rp5.ru/?lang=ru&%s' % (query)).read();
	if(text.count('1. <a href="')):
		idx = re.search('1. <a href="', text).end();
		text = text[idx:]
		idx = re.search('">', text).start();
		code = text[:idx];

		rawXml = minidom.parse(urllib.urlopen('http://rp5.ru/rss/%s' % (code)));
		message, city = '', None;
		for x in rawXml.getElementsByTagName('item'):
			title = x.getElementsByTagName('title')[0].firstChild.data.strip().split(': ', 1);
			desc = x.getElementsByTagName('description')[0].firstChild.data.strip();
			city = title[0];
			desc = desc.replace('%)', '%')
			desc = desc.replace(' (', ', ');
			desc = desc.replace(')', '');
			message += u'[%s]\nТемпература: %s\n\n' % (title[1], desc);
		if(message):
			message = u'Погода в городе %s\n%s' % (city, message);
			if(PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u'скинула в личку');
			sendMsg(PRIVATE, conference, nick, message);
		else:
			sendMsg(msgType, conference, nick, u'не могу :(');
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');

registerCommand(showWeather, u'погода', 10, u'Показывает погоду', u'погода <город>', (u'погода Москва', ), ANY | PARAM);
