# coding: utf-8;

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

def setUserRole(conference, param, role):
	param = param.split();
	nick = param[0];	
	if(nick.count('@') or nickInConference(conference, nick)):
		reason = (len(param) > 1) and ' '.join(param[1:]) or '';
		setRole(conference, nick, role, reason);
		return(True);
	return(False);
	
def setUserAffiliation(conference, param, aff):
	param = param.split();
	nick = param[0];	
	if(nick.count('@') or nickInConference(conference, nick)):
		reason = (len(param) > 1) and ' '.join(param[1:]) or '';
		setAffiliation(conference, nick, aff, reason);
		return(True);
	return(False);

def setOutcast(msgType, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_OUTCAST)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setNone(msgType, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_NONE)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setMember(msgType, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_MEMBER)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setAdmin(msgType, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_ADMIN)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setOwner(msgType, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_OWNER)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
	
def setKick(msgType, conference, nick, param):
	if(setUserRole(conference, param, ROLE_NONE)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
		
def setVisitor(msgType, conference, nick, param):
	if(setUserRole(conference, param, ROLE_VISITOR)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setParticipant(msgType, conference, nick, param):
	if(setUserRole(conference, param, ROLE_PARTICIPANT)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

def setModerator(msgType, conference, nick, param):
	if(setUserRole(conference, param, ROLE_MODERATOR)):
		sendMsg(msgType, conference, nick, u'сделала');
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');

registerCommand(setOutcast, u'бан', 20, u'Банит пользователя', u'бан <ник/жид>', (u'бан bot@freize.org', u'бан Nick'), CHAT | PARAM);
registerCommand(setNone, u'избани', 20, u'Разбанивает пользователя', u'избани <ник/жид>', (u'избани bot@freize.org', u'избани Nick'), CHAT | PARAM);
registerCommand(setMember, u'мембер', 20, u'Дает мембера', u'мембер <ник/жид>', (u'мембер bot@freize.org', u'мембер Nick'), CHAT | PARAM);
registerCommand(setAdmin, u'админ', 30, u'Дает админа', u'админ <ник/жид>', (u'админ bot@freize.org', u'админ Nick'), CHAT | PARAM);
registerCommand(setOwner, u'овнер', 30, u'Дает овнера', u'овнер <ник/жид>', (u'овнер bot@freize.org', u'овнер Nick'), CHAT | PARAM);
registerCommand(setKick, u'кик', 15, u'Кикает', u'кик <ник/жид>', (u'кик bot@freize.org', u'кик Nick'), CHAT | PARAM);
registerCommand(setVisitor, u'девойс', 15, u'Отнимает голос', u'девойс <ник/жид>', (u'девойс bot@freize.org', u'девойс Nick'), CHAT | PARAM);
registerCommand(setParticipant, u'войс', 15, u'Даёт голос', u'войс <ник/жид>', (u'войс bot@freize.org', u'войс Nick'), CHAT | PARAM);
registerCommand(setModerator, u'модер', 20, u'Даёт модера', u'модер <ник/жид>', (u'модер bot@freize.org', u'модер Nick'), CHAT | PARAM);
