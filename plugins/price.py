# coding: utf-8

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
	domen = netutil.quote(param)
	url = "http://www.webvaluer.org/ru/www.%s" % (domen)
	response = netutil.getURL(url)
	if response:
		rawhtml = response.read()
		elements = re.search(r"<td class=\"value\">(.+?)</td>", rawhtml, re.DOTALL)
		if elements:
			cost = unicode(elements.group(1), "utf-8")
			cost = cost.split()
			if len(cost) == 2:
				cost = "%s %s" % (cost[1], cost[0])
			else:
				cost = cost[0]
			sendMsg(msgType, conference, nick, u"Стоимость домена %s составляет %s" %  (param, cost))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showPrice, u"домен", 10, 
				u"Показывает оценочную стоимость домена", 
				u"<запрос>", 
				(u"server.tld", ), 
				CMD_ANY | CMD_PARAM)
