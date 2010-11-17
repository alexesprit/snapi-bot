# coding: utf-8

# facts.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showFact(msgType, conference, nick, param):
	pageNum = random.randrange(1, 29)
	url = "http://skio.ru/facts/fact%d.php" % (pageNum)
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search("<div style=.+?<ul>(.+?)</ul>", rawhtml, re.DOTALL)
		if items:
			rawhtml = items.group(1)
			items = re.findall("<li>(.+?)</li>", rawhtml, re.DOTALL)
			fact = random.choice(items)
			sendMsg(msgType, conference, nick, decode(fact, "cp1251"))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showFact, u"факт", 10, 
				u"Показывает случайный интересный факт", 
				None, 
				None, 
				ANY | NONPARAM)
