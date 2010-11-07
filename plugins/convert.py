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
				count = float(param[2])
			except ValueError:
				sendMsg(msgType, conference, nick, u"Читай помощь по команде")
				return
			source = param[0]
			target = param[1]
			if source in CONV_VALUES and target in CONV_VALUES:
				date = tuple(time.localtime())[1:3]
				url = "http://conv.rbc.ru/convert.shtml?tid_from=%s&tid_to=%s&summa=%s&day=%s&month=%s"
				url %= (source, target, count, date[1], date[0])
				rawhtml = urllib.urlopen(url.replace("RUR", "BASE")).read()
				rawhtml = unicode(rawhtml, "cp1251")
				items = re.search("<TD><B>.+?</B>.+?<TD><B>(.+?)</B>.+?<TD><B>(.+?)</B></TD>", rawhtml, re.DOTALL)
				if items:
					message = u"%s %s = %s %s\n1 %s = %s %s" % (count, source, items.group(2), target, source, items.group(1), target)
					message = message.replace("BASE", "RUR")
					sendMsg(msgType, conference, nick, message)
				else:
					sendMsg(msgType, conference, nick, u"Не получается")
			else:
				sendMsg(msgType, conference, nick, u"Читай помощь по команде")

registerEvent(loadValuesForConvert, STARTUP)

registerCommand(convertValues, u"перевести", 10, 
				u"Перевод валют. Указав \"валюты\" в кач-ве параметра можно посмотреть доступные валюты для перевода", 
				u"перевести <из> <в> <кол-во>", 
				(u"перевести валюты", u"перевести RUR USD 100.5"), 
				ANY | PARAM)
