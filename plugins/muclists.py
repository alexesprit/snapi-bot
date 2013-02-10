# coding: utf-8

# muclists.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showMUCList(msgType, conference, nick, aff):
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_MUC_ADMIN)
	iq.setQueryPayload([protocol.Node("item", {"affiliation": aff})])
	iq.setTo(conference)
	iq.setID(getUniqueID("muc_id"))
	gClient.sendAndCallForResponse(iq, showMUCList_, (msgType, conference, nick))

def showMUCList_(stanza, msgType, conference, nick):
	if protocol.TYPE_RESULT == stanza.getType():
		elements = []
		for i, child in enumerate(stanza.getQueryChildren()):
			jid = child.getAttr("jid")
			reason = child.getTagData("reason")
			if reason:
				elements.append(u"%d) %s (%s)" % (i + 1, jid, reason.strip()))
			else:
				elements.append(u"%d) %s" % (i + 1, jid))
		if elements:
			if msgType == protocol.TYPE_PUBLIC:
				sendMsg(msgType, conference, nick, u"Ушёл")
			message = u"Смотри, что я нашла:\n%s" % ("\n".join(elements))
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Список пуст")
	else:
		sendMsg(msgType, conference, nick, u"Не могу :(")

def showOutcastsList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_OUTCAST)

def showMembersList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_MEMBER)

def showAdminsList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_ADMIN)

def showOwnersList(msgType, conference, nick, param):
	showMUCList(msgType, conference, nick, protocol.AFF_OWNER)

registerCommand(showOutcastsList, u"банлист", 20, 
				u"Показывает список забаненных участников конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showMembersList, u"мемберлист", 20, 
				u"Показывает список постоянных участников конференции", 
				None, 
				None,  
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showAdminsList, u"админлист", 20, 
				u"Показывает список администраторов конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showOwnersList, u"овнерлист", 20, 
				u"Показывает список владельцев конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
