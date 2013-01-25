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
	data = netutil.getURLResponseData(url, qparam, encoding='utf-8')
	if data:
		elements = re.search(r"<div id=\"hypercontext\">(.+?)</div>", data, re.DOTALL)
		message = netutil.removeTags(elements.group(1))
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушёл")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showDreamInfo, u"сонник", 10, 
				u"Толкователь снов", 
				u"<что-то>", 
				(u"деньги", ), 
				CMD_ANY | CMD_PARAM)
