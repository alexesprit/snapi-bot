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

AFOR_PAGES = (
		'biz_quotes.php',
		'rich_quotes.php',
		'family_quotes.php',
		'kids_quotes.php',
		'friend_quotes.php',
		'human_quotes.php',
		'health_quotes.php',
		'beauty_quotes.php',
		'love_quotes.php',
		'world_quotes.php',
		'wisdom_quotes.php',
		'menwomen_quotes.php',
		'science_quotes.php',
		'edu_quotes.php',
		'pessimism_quotes.php',
		'politics_quotes.php',
		'truth_quotes.php',
		'religion_quotes.php',
		'death_quotes.php',
		'happy_quotes.php',
		'work_quotes.php',
		'humour_quotes.php',
);

def showAforism(msgType, conference, nick, param):
	randPage = random.choice(AFOR_PAGES);
	rawHtml = urllib.urlopen('http://skio.ru/quotes/%s' % (randPage)).read();
	items = re.search('<form id="qForm" method="post"><div align="center">(.+?)</div>', rawHtml, re.DOTALL);
	if(items):
		aforism = decode(items.group(0));
		sendMsg(msgType, conference, nick, unicode(aforism, 'cp1251'));
	else:
		sendMsg(msgType, conference, nick, u'не получается');

registerCommand(showAforism, u'афор', 10, u'Показывает случайный афоризм', None, (u'афор', ), ANY | NONPARAM);
