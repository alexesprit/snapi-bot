# coding: utf-8;

# whois.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showWhoIs(type, conference, nick, param):
	rawHtml = urllib.urlopen('http://1whois.ru/index.php?url=%s' % (param)).read();
	print rawHtml;
	items = re.search('<blockquote>(.*?)</font></blockquote>', rawHtml, re.DOTALL);
	if(items):
		text = items.group(0);
		text = text.replace('<br />', '');
		text = text.replace('&nbsp;', '');
		text = decode(text);
		sendMsg(type, conference, nick, unicode(text, 'cp1251'));
	else:
		sendMsg(type, conference, nick, u'не могу :(');

registerCommand(showWhoIs, u'хтоэто', 10, u'Показывает информацию о домене', u'хтоэто <адрес>', (u'хтоэто jabber.ru', ), ANY | PARAM);
