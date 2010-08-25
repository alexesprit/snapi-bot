# coding: utf-8;

# dreams.py
# Initial Copyright (c) Avinar <avinar@xmpp.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showDreamInfo(type, conference, nick, param):
	query = urllib.urlencode({'key' : param.encode('cp1251')});
	text = unicode(urllib.urlopen('http://www.sonnik.ru/search.php?%s' % (query)).read(), 'windows-1251');
	items = re.search(r'<div id="mntxt">(.*?)</p>', text, re.DOTALL);
	text = decode(items.group(0));
	if(PUBLIC == type):
		sendMsg(type, conference, nick, u'ушло в приват');
	sendMsg(PRIVATE, conference, nick, text);

registerCommand(showDreamInfo, u'сонник', 10, u'Толкователь снов', u'сонник <что-то>', (u'сонник деньги', ), ANY | PARAM);
