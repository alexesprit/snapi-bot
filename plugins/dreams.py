# coding: utf-8

# dreams.py
# Initial Copyright (c) Avinar <avinar@protocol.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showDreamInfo(msgType, conference, nick, param):
	query = urllib.urlencode({"key" : param.encode("cp1251")})
	url = "http://www.sonnik.ru/search.php?%s" % (query)
	rawHTML = urllib.urlopen(url).read()
	items = re.search(r"<div id=\"mntxt\">(.+?)</p>", rawHTML, re.DOTALL)
	message = decode(items.group(0))
	if(protocol.TYPE_PUBLIC == msgType):
		sendMsg(msgType, conference, nick, u"ушло в приват")
	sendMsg(protocol.TYPE_PRIVATE, conference, nick, unicode(message, "cp1251"))

registerCommand(showDreamInfo, u"сонник", 10, 
				u"Толкователь снов", 
				u"сонник <что-то>", 
				(u"сонник деньги", ), 
				ANY | PARAM)
