# coding: utf-8

# decipher.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>

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
		sendMsg(msgType, conference, nick, u"Что-то ты многовато написал")
	elif len(param) < 2:
		sendMsg(msgType, conference, nick, u"Что так мало?")
	else:
		query = urllib.urlencode({"word" : param.lower().encode("cp1251")})
		url = "http://combats.stalkers.ru/?a=analiz_nick&%s" % (query)
		rawHTML = urllib.urlopen(url).read()
		items = re.search(r"<div style='text-align:center;'><b>(.*?)</b></div>", rawHTML, re.DOTALL)
		if items:
			text = items.group(1)
			sendMsg(msgType, conference, nick, unicode(text, "cp1251"))
		else:
			sendMsg(msgType, conference, nick, u"Не получается")

registerCommand(decipherExpression, u"шифр", 10, 
				u"Расшифровывает слово", 
				u"шифр <слово>", 
				(u"шифр админ", ), 
				ANY | PARAM)
