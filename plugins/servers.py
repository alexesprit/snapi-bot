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

def _showServerStats(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		items = []
		for stat in stanza.getQueryChildren():
			attrs = stat.getAttrs()
			if len(attrs) == 3:
				items.append(u"%(name)s: %(value)s %(units)s" % (attrs))
		if items:
			message = u"Инфа о %s:\n%s" % (server, "\n".join(items))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def _showServerInfo(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
		iq.setQueryPayload(stanza.getQueryChildren())
		iq.setTo(server)
		iq.setID(getUniqueID("info_id"))
		gClient.sendAndCallForResponse(iq, _showServerStats, (msgType, conference, nick, server))
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerInfo(msgType, conference, nick, param):
	server = param or PROFILE_SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
	iq.setTo(server)
	iq.setID(getUniqueID("info_id"))
	gClient.sendAndCallForResponse(iq, _showServerInfo, (msgType, conference, nick, server))

def _showServerUptime(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		child = stanza.getFirstChild()
		seconds = int(child.getAttr("seconds"))
		if seconds:
			sendMsg(msgType, conference, nick, u"Время работы %s: %s" % (server, getUptimeStr(seconds)))
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerUptime(msgType, conference, nick, param):
	server = param or PROFILE_SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_LAST)
	iq.setTo(server)
	iq.setID(getUniqueID("uptime_id"))
	gClient.sendAndCallForResponse(iq, _showServerUptime, (msgType, conference, nick, server))

registerCommand(showServerInfo, u"инфа", 10, 
				u"Возвращает статистику о сервере", 
				u"[сервер]", 
				(u"server.tld", ))
registerCommand(showServerUptime, u"аптайм", 10, 
				u"Показывает аптайм определённого сервера", 
				u"[сервер]", 
				(u"server.tld", ))
