# coding: utf-8

# horoscope.py
# Initial Copyright (c) esprit

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
	args = param.split()
	sign = args[0].lower()
	if sign in HOROSCOPE_SIGNS:
		rawsign = HOROSCOPE_SIGNS[sign]
		if len(args) > 1:
			date = args[1].lower()
			if date in HOROSCOPE_DATES:
				rawdate = HOROSCOPE_DATES[date]
			else:
				examples = ", ".join(HOROSCOPE_DATES.keys())
				sendMsg(msgType, conference, nick,
					u"В кач-ве дат можно указывать только следующее: %s" % (examples))
				return
		else:
			rawdate = u"today"

		url = "http://img.ignio.com/r/export/utf/xml/daily/com.xml"
		data = netutil.getURLResponseData(url, encoding='raw')
		if data:
			xmlnode = simplexml.XML2Node(data)
			horoNode = xmlnode.getTag(rawsign)
			text = horoNode.getTagData(rawdate)
			date = xmlnode.getTagAttr("date", rawdate)
			sendMsg(msgType, conference, nick, u"Гороскоп на %s: %s" % (date, text))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		examples = ", ".join(sorted(HOROSCOPE_SIGNS.keys()))
		sendMsg(msgType, conference, nick,
			u"Можно указывать только следующие знаки: %s" % (examples))

registerCommand(showHoroscope, u"гороскоп", 10,
				u"Показывает гороскоп для указанного знака гороскопа. Возможен просмотр гороскопа на сегодня, вчера, завтра, послезавтра (указывайте 2-м параметром, без указания покажет для сегодняшнего дня)",
				u"<знак> [день]",
				(u"рыбы", u"рыбы завтра"),
				CMD_ANY | CMD_PARAM)
