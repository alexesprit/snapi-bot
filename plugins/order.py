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

def setUserRole(groupChat, param, role):
	param = param.split();
	nick = param[0];	
	if(nick.count('@') or nickInChat(groupChat, nick)):
		reason = (len(param) > 1) and ' '.join(param[1:]) or '';
		setRole(groupChat, nick, role, reason);
		return(True);
	return(False);
	
def setUserAffiliation(groupChat, param, aff):
	param = param.split();
	nick = param[0];	
	if(nick.count('@') or nickInChat(groupChat, nick)):
		reason = (len(param) > 1) and ' '.join(param[1:]) or '';
		setAffiliation(groupChat, nick, aff, reason);
		return(True);
	return(False);

def setOutcast(type, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_OUTCAST)):
		sendMsg(type, conference, nick, u'сделала');
	
def setNone(type, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_NONE)):
		sendMsg(type, conference, nick, u'сделала');
	
def setMember(type, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_MEMBER)):
		sendMsg(type, conference, nick, u'сделала');
	
def setAdmin(type, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_ADMIN)):
		sendMsg(type, conference, nick, u'сделала');
	
def setOwner(type, conference, nick, param):
	if(setUserAffiliation(conference, param, AFF_OWNER)):
		sendMsg(type, conference, nick, u'сделала');
	
def setKick(type, conference, nick, param):
	if(setUserRole(conference, param, ROLE_NONE)):
		sendMsg(type, conference, nick, u'сделала');
		
def setVisitor(type, conference, nick, param):
	if(setUserRole(conference, param, ROLE_VISITOR)):
		sendMsg(type, conference, nick, u'сделала');
	
def setParticipant(type, conference, nick, param):
	if(setUserRole(conference, param, ROLE_PARTICIPANT)):
		sendMsg(type, conference, nick, u'сделала');

def setModerator(type, conference, nick, param):
	if(setUserRole(conference, param, ROLE_MODERATOR)):
		sendMsg(type, conference, nick, u'сделала');

registerCommandHandler(setOutcast, u'бан', 20, u'Банит пользователя', u'бан <ник/жид>', (u'бан bot@freize.org', u'бан Nick'), CHAT | PARAM);
registerCommandHandler(setNone, u'избани', 20, u'Разбанивает пользователя', u'избани <ник/жид>', (u'избани bot@freize.org', u'избани Nick'), CHAT | PARAM);
registerCommandHandler(setMember, u'мембер', 20, u'Дает мембера', u'мембер <ник/жид>', (u'мембер bot@freize.org', u'мембер Nick'), CHAT | PARAM);
registerCommandHandler(setAdmin, u'админ', 30, u'Дает админа', u'админ <ник/жид>', (u'админ bot@freize.org', u'админ Nick'), CHAT | PARAM);
registerCommandHandler(setOwner, u'овнер', 30, u'Дает овнера', u'овнер <ник/жид>', (u'овнер bot@freize.org', u'овнер Nick'), CHAT | PARAM);
registerCommandHandler(setKick, u'кик', 15, u'Кикает', u'кик <ник/жид>', (u'кик bot@freize.org', u'кик Nick'), CHAT | PARAM);
registerCommandHandler(setVisitor, u'девойс', 15, u'Отнимает голос', u'девойс <ник/жид>', (u'девойс bot@freize.org', u'девойс Nick'), CHAT | PARAM);
registerCommandHandler(setParticipant, u'войс', 15, u'Даёт голос', u'войс <ник/жид>', (u'войс bot@freize.org', u'войс Nick'), CHAT | PARAM);
registerCommandHandler(setModerator, u'модер', 20, u'Даёт модера', u'модер <ник/жид>', (u'модер bot@freize.org', u'модер Nick'), CHAT | PARAM);
