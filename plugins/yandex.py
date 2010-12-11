# coding: utf-8

# yandex.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def searchInYandex(msgType, conference, nick, param):
	url = "http://yandex.ru/msearch"
	qparam = {"query": param.encode("utf-8")}
	response = getURL(url, qparam)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "utf-8")
		elements = re.findall("<li >\n(.+?)\n.+?<div class=\"www\">(.+?)</div>", rawhtml, re.DOTALL)
		if elements:
			if protocol.TYPE_PUBLIC == msgType:
				elements = elements[:1]
			else:
				elements = elements[:5]			
			foundElements = [u"%s\nhttp://%s" % (element[0], element[1]) for element in elements]
			message = "\n\n".join(foundElements)
			sendMsg(msgType, conference, nick, decode(message))
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(searchInYandex, u"яндекс", 10, 
				u"Поиск через Yandex", 
				u"<текст>", 
				(u"google", ), 
				CMD_ANY | CMD_PARAM)
