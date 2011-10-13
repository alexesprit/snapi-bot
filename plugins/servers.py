# coding: utf-8

# servers.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showServerInfo(msgType, conference, nick, param):
	server = param or Config.SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
	iq.setTo(server)
	iq.setID(getUniqueID("info_id"))
	gClient.sendAndCallForResponse(iq, showServerInfo_, (msgType, conference, nick, server))

def showServerInfo_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
		iq.setQueryPayload(stanza.getQueryChildren())
		iq.setTo(server)
		iq.setID(getUniqueID("info_id"))
		gClient.sendAndCallForResponse(iq, showServerStats_, (msgType, conference, nick, server))
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerStats_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		elements = []
		for stat in stanza.getQueryChildren():
			attrs = stat.getAttrs()
			if len(attrs) == 3:
				elements.append(u"%(name)s: %(value)s %(units)s" % (attrs))
		if elements:
			message = u"Инфа о %s:\n%s" % (server, "\n".join(elements))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerUptime(msgType, conference, nick, param):
	server = param or Config.SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_LAST)
	iq.setTo(server)
	iq.setID(getUniqueID("uptime_id"))
	gClient.sendAndCallForResponse(iq, showServerUptime_, (msgType, conference, nick, server))

def showServerUptime_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		child = stanza.getFirstChild()
		seconds = int(child.getAttr("seconds"))
		if seconds:
			sendMsg(msgType, conference, nick, u"Время работы %s: %s" % (server, getUptimeStr(seconds)))
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showServerInfo, u"инфа", 10,
				u"Возвращает статистику jabber-сервера",
				u"[сервер]",
				(u"server.tld", ))
registerCommand(showServerUptime, u"аптайм", 10,
				u"Показывает аптайм jabber-сервера",
				u"[сервер]",
				(u"server.tld", ))
