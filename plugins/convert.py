# coding: utf-8

# convert.py
# Initial Copyright (с) 2010 -Esprit-

# Based on the same plugin of Isida-bot

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CONV_CURRENCIES_FILE = "currencies.txt"

def loadVCurrenciesForConvert():
	global CONV_CURRENCIES
	path = getFilePath(RESOURCE_DIR, CONV_CURRENCIES_FILE)
	CONV_CURRENCIES = eval(utils.readFile(path, "utf-8"))

def convertValues(msgType, conference, nick, param):
	if param.lower() == u"валюты":
		elements = [u"%s - %s" % (desc, name) for name, desc in CONV_CURRENCIES.items()]
		elements.sort()
		sendMsg(msgType, conference, nick, "\n".join(elements))
	else:
		if len(param.split()) == 3:
			param = param.upper().split()
			try:
				value = float(param[2])
			except ValueError:
				sendMsg(msgType, conference, nick, u"Читай помощь по команде")
				return
			source = param[0]
			target = param[1]
			if source and target in CONV_CURRENCIES:
				if source == "RUR":
					source = "BASE"
				if target == "RUR":
					target = "BASE"
				url = "http://conv.rbc.ru/convert.shtml"
				qparam = {
					"tid_from": source,
					"tid_to": target,
					"summa": value
				}
				response = getURL(url, qparam)
				if response:
					rawhtml = response.read()
					elements = re.search("<TD><B>.+?</B>.+?<TD><B>(.+?)</B>.+?<TD><B>(.+?)</B></TD>", rawhtml, re.DOTALL)
					if elements:
						sourceValue = unicode(elements.group(2), "cp1251")
						targetValue = unicode(elements.group(1), "cp1251")
						message = u"%s %s = %s %s\n1 %s = %s %s" % (value, source, sourceValue, target, source, targetValue, target)
						message = message.replace("BASE", "RUR")
						sendMsg(msgType, conference, nick, message)
					else:
						sendMsg(msgType, conference, nick, u"Ошибка!")
				else:
					sendMsg(msgType, conference, nick, u"Ошибка!")
			else:
				sendMsg(msgType, conference, nick, u"Читай помощь по команде")

registerEventHandler(loadVCurrenciesForConvert, EVT_STARTUP)

registerCommand(convertValues, u"перевести", 10, 
				u"Переводит валюты. Чтобы получить список доступных валют для перевода, укажите \"валюты\" в кач-ве параметра",
				u"<из> <в> <кол-во>", 
				(u"валюты", u"RUR USD 100.5"), 
				CMD_ANY | CMD_PARAM)
