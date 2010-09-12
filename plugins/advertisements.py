# coding: utf-8;

# advertisement.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

ADV_COUNT = 12;

def showAdvert(msgType, conference, nick, param):
	pageNum = random.randrange(1, ADV_COUNT + 1);
	rawHtml = urllib.urlopen('http://skio.ru/funnyad/%d.php' % (pageNum)).read();
	items = re.findall('<tr><td>(.+?)</td></tr>', rawHtml, re.DOTALL);
	if(items):
		adv = random.choice(items);
		adv = decode(adv);
		sendMsg(msgType, conference, nick, unicode(adv, 'cp1251'));
	else:
		sendMsg(msgType, conference, nick, u'не получается');

registerCommand(showAdvert, u'объявление', 10, u'Показывает случайное интересное объявление', None, (u'объявление', ), ANY | NONPARAM);
