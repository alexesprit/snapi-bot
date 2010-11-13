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
	qparam = {
		"s": "all",
		"query": param.encode("utf-8")
	}
	responce = getURL(url, qparam)
	if responce:
		rawhtml = responce.read()
		rawhtml = unicode(rawhtml, "utf-8")
		items = re.findall("<li>\n(.+?)<p class=\"b-phone\">.+?<div class=\"www\">(.+?)</div>", rawhtml, re.DOTALL)
		if items:
			if protocol.TYPE_PUBLIC == msgType:
				text = items[0][0].strip()
				url = items[0][1]
				message = u"%s\nhttp://%s" % (text, url)
			else:
				items = [u"%s\nhttp://%s" % (item[0].strip(), item[1]) for item in items[:5]]
				message = "\n\n".join(items)
			sendMsg(msgType, conference, nick, decode(message));	
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(searchInYandex, u"яндекс", 10, 
				u"Поиск через Yandex", 
				u"яндекс <текст>", 
				(u"яндекс google", ), 
				ANY | PARAM)
