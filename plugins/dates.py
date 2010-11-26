# coding: utf-8

# dates.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showDates(msgType, conference, nick, param):
	url = "http://wap.n-urengoy.ru/cgi-bin/wappr.pl"
	response = getURL(url)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "utf-8")
		dates = rawhtml.split("<br/>-----<br/>")
		dates = dates[1:-1]
		if dates:
			dates = [date.split("/")[0] for date in dates]
			sendMsg(msgType, conference, nick, u"Глянь, что я нашла:" + u"\n".join(dates))
		else:
			sendMsg(msgType, conference, nick, u"На сегодня праздников нет")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showDates, u"праздники", 10, 
				u"Показывает праздники на сегодня и завтра", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
