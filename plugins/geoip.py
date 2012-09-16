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
	host = param or Config.HOST
	url = "http://www.and-rey.ru/geoip/ie.php"
	qparam = {"host": host.encode("utf-8")}
	response = netutil.getURL(url, qparam)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "cp1251")
		elements = re.findall("<td class=red>(.+?)</td><td class=blue>(.+?)</td>", rawhtml)
		elements = [u"%s %s" % (element[0], element[1]) for element in elements]
		message = u"Инфо о %s:\n%s" % (host, netutil.decode("\n".join(elements)))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showGeoIPInfo, u"геоип", 10,
				u"Показывает информацию о географическом месторасположении хоста",
				u"[сервер]",
				(None, u"server.tld"))