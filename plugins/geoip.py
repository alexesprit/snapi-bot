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

gGeoIPPattern = re.compile("<td class=red>(.+?)</td><td class=blue>(.+?)</td>")

def showGeoIPInfo(msgType, conference, nick, param):
	host = param or gHost
	query = urllib.urlencode({"host": host.encode("utf-8")})
	url = "http://www.and-rey.ru/geoip/ie.php?%s" % (query)
	rawHTML = urllib.urlopen(url).read()
	rawHTML = unicode(rawHTML, "cp1251")
	items = gGeoIPPattern.findall(rawHTML)
	items = [u"%s %s" % (item[0], item[1]) for item in items]
	message = u"инфо о %s:\n%s" % (host, decode("\n".join(items)))
	sendMsg(msgType, conference, nick, message)

registerCommand(showGeoIPInfo, u"геоип", 10, 
				u"Показывает географическое положение о хосте", 
				u"геоип [сервер]", 
				(u"геоип", u"геоип server.tld"))