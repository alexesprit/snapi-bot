# coding: utf-8

# horoscope.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

SIGNS = {
		u"овен": 1,
		u"телец": 2, 
		u"близнецы": 3, 
		u"рак": 4, 
		u"лев": 5, 
		u"дева": 6, 
		u"весы": 7, 
		u"скорпион": 8, 
		u"стрелец": 9, 
		u"козерог": 10, 
		u"водолей": 11, 
		u"рыбы": 12}

def showHoroscope(msgType, conference, nick, param):
	param = param.lower()
	if(param in SIGNS):
		url = "http://horo.gala.net/?lang=ru&sign=%d" % (SIGNS[param])
		rawHTML = urllib.urlopen(url).read()
		items = re.search(r"<td class=stext>(.+?)</td>", rawHTML, re.DOTALL)
		if(items):
			message = decode(items.group(0), "cp1251")
			if(protocol.TYPE_PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u"ушёл в приват")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"не могу :(")

registerCommand(showHoroscope, u"гороскоп", 10, 
				u"Показывает гороскоп для указанного знака гороскопа", 
				u"гороскоп <знак>", 
				(u"гороскоп рыбы", ), 
				ANY | PARAM)
