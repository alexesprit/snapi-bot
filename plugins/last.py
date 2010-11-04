# coding: utf-8

# last.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showOnlineTime(msgType, jid, resource, param):
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_LAST)
	iq.setTo(jid)
	iq.setID(getUniqueID("last_id"))
	gClient.sendAndCallForResponse(iq, _showOnlineTime, (msgType, jid, resource, ))

def _showOnlineTime(stanza, msgType, jid, resource):
	if protocol.TYPE_RESULT == stanza.getType():
		child = stanza.getFirstChild()
		seconds = child.getAttr("seconds")
		sendMsg(msgType, jid, resource, u"Ты в сети уже %s" % (getTimeStr(int(seconds))))
	else:
		sendMsg(msgType, jid, resource, u"Не получается :(")

registerCommand(showOnlineTime, u"всети", 10, 
				u"Показывает ваше время в сети", 
				None, 
				(u"всети", ), 
				ROSTER | NONPARAM)
