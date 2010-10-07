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

LAST_ID = "last_id"

def showOnlineTime(msgType, jid, resource, param):
	iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_LAST)
	iq.setTo(jid)
	iq.setID(getUniqueID(LAST_ID))
	gClient.SendAndCallForResponse(iq, _showOnlineTime, (msgType, jid, resource, ))

def _showOnlineTime(stanza, msgType, jid, resource):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		child = stanza.getFirstChild()
		seconds = child.getAttr("seconds")
		sendMsg(msgType, jid, resource, u"ты в сети уже %s" % (time2str(int(seconds))))
	else:
		sendMsg(msgType, jid, resource, u"не получается :(")

registerCommand(showOnlineTime, u"всети", 10, 
				u"Показывает ваше время в сети", 
				None, 
				(u"всети", ), 
				ROSTER | NONPARAM)
