# coding: utf-8

# decipher.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def decipherExpression(msgType, conference, nick, param):
	if len(param) > 11:
		sendMsg(msgType, conference, nick, u"Что-то многовато...")
	elif len(param) < 2:
		sendMsg(msgType, conference, nick, u"Что так мало?")
	else:
		url = "http://combats.stalkers.ru/"
		qparam = {
			"a": "analiz_nick",
			"word": param.encode("cp1251")
		}
		data = netutil.getURLResponseData(url, qparam, encoding='windows-1251')
		if data:
			elements = re.search(r"<div style='text-align:center;'><b>(.*?)</b></div>", data, re.DOTALL)
			if elements:
				text = elements.group(1)
				sendMsg(msgType, conference, nick, text)
			else:
				sendMsg(msgType, conference, nick, u"Ошибка!")
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(decipherExpression, u"шифр", 10, 
				u"Расшифровывает слово", 
				u"<слово>", 
				(u"админ", ), 
				CMD_ANY | CMD_PARAM)
