# coding: utf-8

# dreams.py
# Initial Copyright (c) Avinar <avinar@xmpp.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showDreamInfo(msgType, conference, nick, param):
	url = "http://www.sonnik.ru/search.php"
	qparam = {"key": param.encode("cp1251")}
	responce = getURL(url, qparam)
	if responce:
		rawhtml = responce.read()
		items = re.search(r"<div id=\"mntxt\">(.+?)</p>", rawhtml, re.DOTALL)
		message = decode(items.group(1), "cp1251")
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушёл")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
	else:
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Ошибка!")

registerCommand(showDreamInfo, u"сонник", 10, 
				u"Толкователь снов", 
				u"<что-то>", 
				(u"деньги", ), 
				ANY | PARAM)
