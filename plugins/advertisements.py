# coding: utf-8

# advertisements.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showAdvert(msgType, conference, nick, param):
	pageNum = random.randrange(1, 13)
	url = "http://skio.ru/funnyad/%d.php" % (pageNum)
	response = netutil.getURL(url)
	if response:
		rawhtml = response.read()
		elements = re.findall(r"<tr><td>(.+?)</td></tr>", rawhtml, re.DOTALL)
		if elements:
			adv = random.choice(elements)
			adv = decode(adv, "cp1251")
			sendMsg(msgType, conference, nick, adv)
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showAdvert, u"объявление", 10, 
				u"Показывает случайное интересное объявление", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
