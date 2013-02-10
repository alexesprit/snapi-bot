# coding: utf-8

# order.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getUserAndReason(param):
	args = param.split('\n', 1)
	if len(args) == 1:
		return args[0], None
	return args

def setUserRole(msgType, conference, nick, param, role):
	user, reason = getUserAndReason(param)
	if isNickInConference(conference, user):
		iq = getMUCSetRoleStanza(conference, user, role, reason)
		gClient.sendAndCallForResponse(iq, setMUCItem_, (msgType, conference, nick))
	else:
		sendMsg(msgType, conference, nick, u"Чего?")

def setUserAffl(msgType, conference, nick, param, affl):
	user, reason = getUserAndReason(param)
	if isNickInConference(conference, user):
		iq = getMUCSetAfflStanza(conference, user, protocol.ITEM_NICK, affl, reason)
		gClient.sendAndCallForResponse(iq, setMUCItem_, (msgType, conference, nick))
	elif netutil.isJID(user) or netutil.isServer(user):
		iq = getMUCSetAfflStanza(conference, user, protocol.ITEM_JID, affl, reason)
		gClient.sendAndCallForResponse(iq, setMUCItem_, (msgType, conference, nick))	
	else:
		sendMsg(msgType, conference, nick, u"Чего?")

def setMUCItem_(stanza, msgType, conference, nick):
	if protocol.TYPE_RESULT == stanza.getType():
		sendMsg(msgType, conference, nick, u"Сделала")
	else:
		sendMsg(msgType, conference, nick, u"Не могу :(")

def setOutcast(msgType, conference, nick, param):
	setUserAffl(msgType, conference, nick, param, protocol.AFF_OUTCAST)

def setNone(msgType, conference, nick, param):
	setUserAffl(msgType, conference, nick, param, protocol.AFF_NONE)

def setMember(msgType, conference, nick, param): 
	setUserAffl(msgType, conference, nick, param, protocol.AFF_MEMBER)

def setAdmin(msgType, conference, nick, param):
	setUserAffl(msgType, conference, nick, param, protocol.AFF_ADMIN)

def setOwner(msgType, conference, nick, param):
	setUserAffl(msgType, conference, nick, param, protocol.AFF_OWNER)
	
def setKick(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, protocol.ROLE_NONE)
		
def setVisitor(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, protocol.ROLE_VISITOR)

def setParticipant(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, protocol.ROLE_PARTICIPANT)

def setModerator(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, protocol.ROLE_MODERATOR)

registerCommand(setOutcast, u"бан", 20, 
				u"Добавляет пользователя в список забаненных участников", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setNone, u"избани", 20, 
				u"Удаляет пользователя из списка забаненных участников", 
				u"<ник/жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setMember, u"мембер", 20, 
				u"Добавляет пользователя в список постоянных участников", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setAdmin, u"админ", 30, 
				u"Добавляет пользователя в список администраторов конференции", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setOwner, u"овнер", 30, 
				u"Добавляет пользователя в список владельцев конференции", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setKick, u"кик", 15, 
				u"Выгоняет пользователя из конференции", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setVisitor, u"девойс", 15, 
				u"Лишает участника конференции голоса", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setParticipant, u"войс", 15, 
				u"Даёт участнику конференции право голоса", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setModerator, u"модер", 20, 
				u"Даёт участнику право модерировать коференцию", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
