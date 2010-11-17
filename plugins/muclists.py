# coding: utf-8

# muclists.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def _showMUCList(stanza, msgType, conference, nick):
	if protocol.TYPE_RESULT == stanza.getType():
		items = [u"%d) %s" % (i + 1, p.getAttrs()["jid"]) for i, p in enumerate(stanza.getQueryChildren())]
		if items:
			message = u"Смотри, что я нашла:\n"
			if msgType == protocol.TYPE_PUBLIC:
				sendMsg(msgType, conference, nick, u"Ушёл")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message + "\n".join(items))
		else:
			sendMsg(msgType, conference, nick, u"Список пуст")
	else:
		sendMsg(msgType, conference, nick, u"Не могу :(")

def showMUCList(msgType, conference, nick, aff):
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_MUC_ADMIN)
	iq.setQueryPayload([protocol.Node("item", {"affiliation": aff})])
	iq.setTo(conference)
	iq.setID(getUniqueID("muc_id"))
	gClient.sendAndCallForResponse(iq, _showMUCList, (msgType, conference, nick))

def showOutcastsList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_OUTCAST)

def showMembersList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_MEMBER)

def showAdminsList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_ADMIN)

def showOwnersList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_OWNER)

registerCommand(showOutcastsList, u"банлист", 20, 
				u"Показывает список забаненных", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showMembersList, u"мемберлист", 20, 
				u"Показывает список мемберов", 
				None, 
				None,  
				CHAT | NONPARAM)
registerCommand(showAdminsList, u"админлист", 20, 
				u"Показывает список админов", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showOwnersList, u"овнерлист", 20, 
				u"Показывает список овнеров", 
				None, 
				None, 
				CHAT | NONPARAM)
