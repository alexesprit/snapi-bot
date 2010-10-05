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

INFO_ID = "info_id"
STATS_ID = "stats_id"
UPTIME_ID = "uptime_id"

def _showServerStats(stanza, msgType, conference, nick, server):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		items = []
		for stat in stanza.getQueryChildren():
			attrs = stat.getAttrs()
			if(len(attrs) == 3):
				items.append(u"%(name)s: %(value)s %(units)s" % (attrs))
		if(items):
			message = u"Инфа о %s:\n%s" % (server, "\n".join(items))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"пустая инфа")
	else:
		sendMsg(msgType, conference, nick, u"не получается :(")

def _showServerInfo(stanza, msgType, conference, nick, server):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_STATS)
		iq.setQueryPayload(stanza.getQueryChildren())
		iq.setTo(server)
		iq.setID(getUniqueID(STATS_ID))
		gClient.SendAndCallForResponse(iq, _showServerStats, (msgType, conference, nick, server, ))
	else:
		sendMsg(msgType, conference, nick, u"не получается :(")

def showServerInfo(msgType, conference, nick, param):
	server = param or gHost
	iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_STATS)
	iq.setTo(server)
	iq.setID(getUniqueID(INFO_ID))
	gClient.SendAndCallForResponse(iq, _showServerInfo, (msgType, conference, nick, server, ))

def _showServerUptime(stanza, msgType, conference, nick, server):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		child = stanza.getFirstChild()
		seconds = child.getAttr("seconds")
		sendMsg(msgType, conference, nick, u"%s работает уже %s" % (server, time2str(int(seconds))))
	else:
		sendMsg(msgType, conference, nick, u"не получается :(")

def showServerUptime(msgType, conference, nick, param):
	server = param or gHost
	iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_LAST)
	iq.setTo(server)
	iq.setID(getUniqueID(UPTIME_ID))
	gClient.SendAndCallForResponse(iq, _showServerUptime, (msgType, conference, nick, server, ))

registerCommand(showServerInfo, u"инфа", 10, 
				u"Возвращает статистику о сервере", 
				u"инфа [сервер]", 
				(u"инфа server.tld", ))
registerCommand(showServerUptime, u"аптайм", 10, 
				u"Показывает аптайм определённого сервера", 
				u"аптайм [сервер]", 
				(u"аптайм server.tld", ))
