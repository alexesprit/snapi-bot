# coding: utf-8

# geoip.py
# Show geographical information about host
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showGeoIPInfo(msgType, conference, nick, param):
	host = param or gHost
	url = "http://www.and-rey.ru/geoip/ie.php"
	qparam = {"host": host.encode("utf-8")}
	responce = getURL(url, qparam)
	if responce:
		rawhtml = responce.read()
		rawhtml = unicode(rawhtml, "cp1251")
		items = re.findall("<td class=red>(.+?)</td><td class=blue>(.+?)</td>", rawhtml)
		items = [u"%s %s" % (item[0], item[1]) for item in items]
		message = u"Инфо о %s:\n%s" % (host, decode("\n".join(items)))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showGeoIPInfo, u"геоип", 10, 
				u"Показывает информацию о географическом месторасположении хоста", 
				u"[сервер]", 
				(None, u"server.tld"))