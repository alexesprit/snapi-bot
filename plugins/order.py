# coding: utf-8

# order.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setUserRole(msgType, conference, nick, user, role):
	if(user.count("@") or nickInConference(conference, user)):
		setRole(conference, user, role)
		sendMsg(msgType, conference, nick, u"сделала")
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")
	
def setUserAffiliation(msgType, conference, nick, user, aff):
	if(user.count("@") or nickInConference(conference, user)):
		setAffiliation(conference, user, aff)
		sendMsg(msgType, conference, nick, u"сделала")
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")

def setOutcast(msgType, conference, nick, param):
	setUserAffiliation(msgType, conference, nick, param, xmpp.AFF_OUTCAST)

def setNone(msgType, conference, nick, param):
	setUserAffiliation(msgType, conference, nick, param, xmpp.AFF_NONE)

def setMember(msgType, conference, nick, param): 
	setUserAffiliation(msgType, conference, nick, param, xmpp.AFF_MEMBER)

def setAdmin(msgType, conference, nick, param):
	setUserAffiliation(msgType, conference, nick, param, xmpp.AFF_ADMIN)

def setOwner(msgType, conference, nick, param):
	setUserAffiliation(msgType, conference, nick, param, xmpp.AFF_OWNER)
	
def setKick(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, xmpp.ROLE_NONE)
		
def setVisitor(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, xmpp.ROLE_VISITOR)

def setParticipant(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, xmpp.ROLE_PARTICIPANT)

def setModerator(msgType, conference, nick, param):
	setUserRole(msgType, conference, nick, param, xmpp.ROLE_MODERATOR)

registerCommand(setOutcast, u"бан", 20, 
				u"Банит пользователя", 
				u"бан <ник|жид>", 
				(u"бан bot@freize.org", u"бан Nick"), 
				CHAT | PARAM)
registerCommand(setNone, u"избани", 20, 
				u"Разбанивает пользователя", 
				u"избани <ник/жид>", 
				(u"избани bot@freize.org", u"избани Nick"), 
				CHAT | PARAM)
registerCommand(setMember, u"мембер", 20, 
				u"Дает мембера", 
				u"мембер <ник|жид>", 
				(u"мембер bot@freize.org", u"мембер Nick"), 
				CHAT | PARAM)
registerCommand(setAdmin, u"админ", 30, 
				u"Дает админа", 
				u"админ <ник|жид>", 
				(u"админ bot@freize.org", u"админ Nick"), 
				CHAT | PARAM)
registerCommand(setOwner, u"овнер", 30, 
				u"Дает овнера", 
				u"овнер <ник|жид>", 
				(u"овнер bot@freize.org", u"овнер Nick"), 
				CHAT | PARAM)
registerCommand(setKick, u"кик", 15, 
				u"Кикает", 
				u"кик <ник|жид>", 
				(u"кик bot@freize.org", u"кик Nick"), 
				CHAT | PARAM)
registerCommand(setVisitor, u"девойс", 15, 
				u"Отнимает голос", 
				u"девойс <ник|жид>", 
				(u"девойс bot@freize.org", u"девойс Nick"), 
				CHAT | PARAM)
registerCommand(setParticipant, u"войс", 15, 
				u"Даёт голос", 
				u"войс <ник|жид>", 
				(u"войс bot@freize.org", u"войс Nick"), 
				CHAT | PARAM)
registerCommand(setModerator, u"модер", 20, 
				u"Даёт модера", 
				u"модер <ник|жид>", 
				(u"модер bot@freize.org", u"модер Nick"), 
				CHAT | PARAM)
