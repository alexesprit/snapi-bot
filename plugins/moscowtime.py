# coding: utf-8

# moscowtime.py
# Copyright (c) ferym <ferym@jabbim.org.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

WEEKDAYS = (u"понедельник", u"вторник", u"среда", u"четверг", u"пятница", u"суббота", u"воскресенье")

def showMoscowTime(msgType, conference, nick, param):
	url = "http://www.zln.ru/time/"
	response = getURL(url)
	if response:
		rawhtml = response.read()
		elements = re.search(r"<div id=\"servertime.+?>(.+?)</div>", rawhtml, re.DOTALL)
		if elements:
			mskTime = unicode(elements.group(1), "cp1251").strip()
			message = u"Московское время: %s (%s, %s)" % (mskTime, time.strftime("%d.%m.%y"), WEEKDAYS[time.localtime()[6]])
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Не получается")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showMoscowTime, u"время", 10, 
				u"Показывает точное московское время", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
