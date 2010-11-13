# coding: utf-8

# convert.py 
# Based on convert.py from Isida-bot
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CONV_VALUES_FILE = "convvalues.txt"

def loadValuesForConvert():
	global CONV_VALUES
	path = getFilePath(RESOURCE_DIR, CONV_VALUES_FILE)
	CONV_VALUES = eval(utils.readFile(path, "utf-8"))

def convertValues(msgType, conference, nick, param):
	if param.lower() == u"валюты":
		values = [u"%s - %s" % (name, desc) for name, desc in CONV_VALUES.items()]
		values.sort()
		sendMsg(msgType, conference, nick, "\n".join(values))
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
			if source in CONV_VALUES and target in CONV_VALUES:
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
				responce = getURL(url, qparam)
				if responce:
					rawhtml = responce.read()
					items = re.search("<TD><B>.+?</B>.+?<TD><B>(.+?)</B>.+?<TD><B>(.+?)</B></TD>", rawhtml, re.DOTALL)
					if items:
						sourceValue = unicode(items.group(2), "cp1251")
						targetValue = unicode(items.group(1), "cp1251")
						message = u"%s %s = %s %s\n1 %s = %s %s" % (value, source, sourceValue, target, source, targetValue, target)
						message = message.replace("BASE", "RUR")
						sendMsg(msgType, conference, nick, message)
					else:
						sendMsg(msgType, conference, nick, u"Ошибка!")
				else:
					sendMsg(msgType, conference, nick, u"Ошибка!")
			else:
				sendMsg(msgType, conference, nick, u"Читай помощь по команде")

registerEvent(loadValuesForConvert, STARTUP)

registerCommand(convertValues, u"перевести", 10, 
				u"Перевод валют. Указав \"валюты\" в кач-ве параметра можно посмотреть доступные валюты для перевода", 
				u"перевести <из> <в> <кол-во>", 
				(u"перевести валюты", u"перевести RUR USD 100.5"), 
				ANY | PARAM)
