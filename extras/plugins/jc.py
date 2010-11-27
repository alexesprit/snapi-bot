# coding: utf-8

# jc.py
# Initial Copyright (с) 2010 -Esprit-

# Отображение рейтинга конференции, используя jc.jabber.ru

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showConferenceRating(msgType, conference, nick, param):
	if not param:
		if isConferenceInList(conference):
			conf = conference.split("@")[0]
		else:
			sendMsg(msgType, conference, nick, u"Необходимо указать конференцию!")
			return
	else:
		conf = param
	url = "http://jc.jabber.ru/search.html"
	qparam = {"search": conf.encode("utf-8")}
	response = getURL(url, qparam)
	if response:
		rawhtml = response.read().decode("utf-8")
		pattern = r"<li>.+?<font color.+?>(.+?)</font>(.+?)</font>"
		elements = re.findall(pattern, rawhtml, re.DOTALL)
		if elements:
			foundElements = []
			for element in elements:
				conf = element[0]
				text = decode(element[1]).strip()
				foundElements.append(u"%s\n%s" % (conf, text))
			message = u"Вот, что я нашла:\n%s" % ("\n\n".join(foundElements))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showConferenceRating, u"jc", 10, 
				u"Показывает рейтинг конференции. Указывать нужно название конференции (до \"@\")", 
				u"[название]", 
				(None, u"room"))
