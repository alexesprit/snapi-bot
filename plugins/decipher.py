# coding: utf-8;

# decipher.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def decipherExpression(type, conference, nick, param):
	if(len(param) > 11):
		sendMsg(type, conference, nick, u'что-то ты многовато написал');
	elif(len(param) < 2):
		sendMsg(type, conference, nick, u'что так мало?');
	else:
		query = urllib.urlencode({'word' : param.lower().encode('cp1251')});
		rawHtml = urllib.urlopen('http://combats.stalkers.ru/?a=analiz_nick&%s' % (query)).read();
		items = re.search("<tr><td><div style='text-align:center;'><b>(.*?)</b></div></td></tr></table><center>", rawHtml, re.DOTALL);
		if(items):
			text = decode(items.group(0));
			sendMsg(type, conference, nick, unicode(text, 'windows-1251'));
		else:
			sendMsg(type, conference, nick, u'не получается');

registerCommandHandler(decipherExpression, u'шифр', 10, u'Расшифровывает слово', u'шифр <слово>', (u'шифр админ', ), ANY | PARAM);
