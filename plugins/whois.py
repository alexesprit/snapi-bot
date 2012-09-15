# coding: utf-8

# whois.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showWhoIs(msgType, conference, nick, param):
	url = "http://1whois.ru/index.php"
	qparam = {"url": param.encode("utf-8")}
	response = netutil.getURL(url, qparam)
	if response:
		rawhtml = response.read()
		elements = re.search("<blockquote>(.+?)</font></blockquote>", rawhtml, re.DOTALL)
		if elements:
			text = elements.group(1)
			text = text.replace("<br />", "")
			text = decode(text, "cp1251")
			sendMsg(msgType, conference, nick, text)
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showWhoIs, u"хтоэто", 10, 
				u"Показывает информацию о домене", 
				u"<адрес>", 
				(u"server.tld", ), 
				CMD_ANY | CMD_PARAM)
