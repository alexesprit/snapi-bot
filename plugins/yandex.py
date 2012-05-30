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
	url = "http://yandex.ru/yandsearch"
	qparam = {"text": param.encode("utf-8")}
	response = getURL(url, qparam)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "utf-8")
		elements = re.findall(r'<a class="b-serp-item__title.+?href="(.+?)".+?>(.+?)</a>.+?<div class="b-serp-item__text">(.+?)</div>', rawhtml, re.DOTALL)
		if elements:
			if protocol.TYPE_PUBLIC == msgType:
				elements = elements[:1]
			else:
				elements = elements[:5]			
			found = []
			for element in elements:
				title = element[1]
				text = element[2].replace("<br/>", "").strip()
				url = element[0]
				result = "%s\n%s\n%s" % (title, text, url)
				result = result.replace(u"<b>", u"«").replace(u"</b>", u"»")
				found.append(result)
			sendMsg(msgType, conference, nick, decode("\n\n".join(found)))
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(searchInYandex, u"яндекс", 10, 
				u"Показывает результаты поиска через Yandex",
				u"<текст>", 
				(u"google", ), 
				CMD_ANY | CMD_PARAM)
