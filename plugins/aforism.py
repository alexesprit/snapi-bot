# coding: utf-8;

# aforism.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showAforism(type, conference, nick, param):
	rawHtml = urllib.urlopen('http://skio.ru/quotes/humour_quotes.php').read();
	items = re.search('<form id="qForm" method="post"><div align="center">(.*?)</div>', rawHtml, re.DOTALL);
	if(items):
		aforism = decode(items.group(0));	
		sendMsg(type, conference, nick, unicode(aforism, 'windows-1251'));
	else:
		sendMsg(type, conference, nick, u'не получается');

registerCommand(showAforism, u'афор', 10, u'Показывает случайный афоризм', None, (u'афор', ), ANY | NONPARAM);
