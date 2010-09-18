# coding: utf-8;

# price.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showPrice(msgType, conference, nick, param):
	rawHtml = urllib.urlopen('http://www.webvaluer.org/ru/www.%s' % (urllib.quote(param.encode('utf-8')))).read();
	items = re.search('<td class="value">(.+?)</td>', rawHtml, re.DOTALL);
	if(items):
		cost = unicode(decode(items.group(0)), 'utf-8');
		cost = cost.split();
		if(len(cost) == 2):
			cost = '%s %s' % (cost[1], cost[0]);
		else:
			cost = cost[0];
		sendMsg(msgType, conference, nick, u'Оценочная стоимость домена %s составляет %s' %  (param, cost));
	else:
		sendMsg(msgType, conference, nick, u'не получается :(');

registerCommand(showPrice, u'домен', 10, u'Показывает оценочную стоимость домена', u'домен <запрос>', (u'домен microsoft.com', ), ANY | PARAM)
