# coding: utf-8

# horoscope.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

HOROSCOPE_SIGNS = {
	u"овен": u"aries", 
	u"телец": u"taurus", 
	u"близнецы": u"gemini", 
	u"рак": u"cancer", 
	u"лев": u"leo", 
	u"дева": u"virgo", 
	u"весы": u"libra", 
	u"скорпион": u"scorpio", 
	u"стрелец": u"sagittarius", 
	u"козерог": u"capricorn", 
	u"водолей": u"aquarius", 
	u"рыбы": u"pisces"
}

HOROSCOPE_DATES = {
	u"вчера": u"yesterday", 
	u"сегодня": u"today", 
	u"завтра": u"tomorrow", 
	u"послезавтра": u"tomorrow02"
}

def showHoroscope(msgType, conference, nick, param):
	param = param.split()
	sign = param[0].lower()
	if sign in HOROSCOPE_SIGNS:
		rawsign = HOROSCOPE_SIGNS[sign]
		if len(param) > 1:
			date = param[1].lower()
			if date in HOROSCOPE_DATES:
				rawdate = HOROSCOPE_DATES[date]
			else:
				message = u"Можно указывать только следующее в кач-ве дат: %s" % (", ".join(HOROSCOPE_DATES.keys()))
				sendMsg(msgType, conference, nick, message)
				return
		else:
			rawdate = u"today"

		url = "http://img.ignio.com/r/export/utf/xml/daily/com.xml"
		responce = getURL(url)
		if responce:
			rawxml = responce.read()
			xmlnode = simplexml.XML2Node(rawxml)
			
			horoNode = xmlnode.getTag(rawsign)
			text = horoNode.getTagData(rawdate)
			date = xmlnode.getTagAttr("date", rawdate)
			sendMsg(msgType, conference, nick, u"Гороскоп на %s: %s" % (date, text))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		message = u"Можно указывать только следующие знаки: %s" % (", ".join(sorted(HOROSCOPE_SIGNS.keys())))
		sendMsg(msgType, conference, nick, message)

registerCommand(showHoroscope, u"гороскоп", 10, 
				u"Показывает гороскоп для указанного знака гороскопа. Возможен просмотр гороскопа на сегодня, вчера, завтра, послезавтра (указывайте 2-м параметром, без указания покажен для сегодняшнего дня)", 
				u"гороскоп <знак> [день]", 
				(u"гороскоп рыбы", u"гороскоп рыбы завтра"), 
				ANY | PARAM)
