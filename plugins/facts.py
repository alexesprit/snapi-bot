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
	data = netutil.getURLResponseData(url)
	if data:
		elements = re.findall("<li>(.+?)<br><br></li>", data)
		if elements:
			fact = random.choice(elements)
			sendMsg(msgType, conference, nick, netutil.removeTags(fact))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showFact, u"факт", 10, 
				u"Показывает случайный интересный факт", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
