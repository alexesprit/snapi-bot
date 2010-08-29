# coding: utf-8;

# access.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) Als <Als@exploit.in>
# Modification Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

ROLE_NONE = 'none';
ROLE_VISITOR = 'visitor';
ROLE_PARTICIPANT = 'participant';
ROLE_MODERATOR = 'moderator';

AFF_OUTCAST = 'outcast';
AFF_NONE = 'none';
AFF_MEMBER = 'member';
AFF_ADMIN = 'admin';
AFF_OWNER = 'owner';

ROLES = {ROLE_NONE: 0, ROLE_VISITOR: 0, ROLE_PARTICIPANT: 10, ROLE_MODERATOR: 15};
AFFILIATIONS = {AFF_OUTCAST: 0, AFF_NONE: 0, AFF_MEMBER: 1, AFF_ADMIN: 5, AFF_OWNER: 15};
ACCESS_DESC = {-100: u'(игнор)', 0: u'(никто)', 10: u'(юзер)', 11: u'(мембер)', 15: u'(модер)', 16: u'(модер)', 20: u'(админ)', 30: u'(овнер)', 100: u'(админ бота)'};

def changeAccess(stanza, conference, nick, trueJid):
	type = stanza.getType();
	if(ERROR != type):
		if(UNAVAILABLE != type):
			role = stanza.getRole();
			aff = stanza.getAffiliation();
			roleAccess = ROLES[role];
			affAccess = AFFILIATIONS[aff];
			setTempAccess(conference, trueJid, roleAccess + affAccess);
			if(AFF_OUTCAST == aff):
				printf(stanza);
		else:
			for item in getOnlineNicks(conference):
				if(getTrueJid(conference, item) == trueJid):
					return;
			setTempAccess(conference, trueJid);

registerPresenceHandler(changeAccess, CHAT);

def login(type, conference, nick, param):
	if(type == PRIVATE and param == gAdminPass):
		trueJid = getTrueJid(conference, nick);
		setTempGlobalAccess(trueJid, 100);
		sendMsg(PRIVATE, conference, nick, u'пароль принят, полный доступ выдан');

registerCommand(login, u'логин', 0, u'Авторизоваться как админиcтратор бота', u'логин <пароль>', (u'логин мой_пароль', ), ANY | FROZEN | PARAM);

def logout(type, conference, nick, parameters):
	trueJid = getTrueJid(conference, nick);
	setTempGlobalAccess(trueJid);
	sendMsg(type, conference, nick, u'доступ снят');

registerCommand(logout, u'логаут', 0, u'Разлогиниться', u'логаут', (u'логаут', ), ANY | FROZEN | NONPARAM);

def showUserAccess(type, conference, nick, param):
	levelDesc = '';
	if(not param):
		trueJid = getTrueJid(conference, nick);
		level = getAccess(conference, trueJid);	
	else:
		if(conferenceInList(conference) and nickInConference(conference, param)):
			trueJid = getTrueJid(conference, param);
		else:
			return;
	level = getAccess(conference, trueJid);
	if(level in ACCESS_DESC):
		levelDesc = ACCESS_DESC[level];
	sendMsg(type, conference, nick, u'%d %s' % (level, levelDesc));

registerCommand(showUserAccess, u'доступ', 0, u'Показывает уровень доступа определённого пользователя', u'доступ [ник]', (u'доступ', u'доступ Nick'), ANY | FROZEN);

def setLocalAccess(type, conference, nick, param):
	param = param.split();
	access = 0;
	if(len(param) > 1):
		access = param[1];
		if(access.isdigit() and -100 <= int(access) <= 100):
			access = int(access);
		else:
			sendMsg(type, conference, nick, u'ошибочный запрос');
			return;
	userNick = param[0].strip();
	if(nickIsOnline(conference, userNick)):
		myJid = getTrueJid(conference, nick);
		myAccess = getAccess(conference, myJid);
		userJid = getTrueJid(conference, userNick);
		userAccess = getAccess(conference, userJid);
		if(userAccess > myAccess or access > myAccess):
			sendMsg(type, conference, nick, u'недостаточно прав');
			return;
		if(len(param) == 1):
			setPermAccess(conference, userJid);
			sendMsg(type, conference, nick, u'постоянный доступ снят');
		elif(len(param) == 2):
			setTempAccess(conference, userJid, access);
			sendMsg(type, conference, nick, u'доступ выдан до выхода из конференции');
		elif(len(param) == 3):
			setPermAccess(conference, userJid, access)
			sendMsg(type, conference, nick, u'выдан постоянный доступ');

registerCommand(setLocalAccess, u'дать_доступ', 20, u'Устанавливает или снимает (если не писать уровень) уровень доступа для определённого пользователя на определённый уровень. Если указываеться третий параметр, то изменение происходит навсегда', u'дать_доступ <ник> [уровень] [навсегда]', (u'дать_доступ Nick 100', u'дать_доступ Nick 100 1'), CHAT | PARAM);

def setGlobalAccess(type, conference, nick, param):
	param = param.split();
	if(len(param) < 1 or len(param) > 2):
		sendMsg(type, conference, nick, u'ошибочный запрос');
		return;
	userNick = param[0].strip();
	if(conferenceInList(conference)):
		if(nickInConference(conference, userNick)):
			trueJid = getTrueJid(conference, userNick);
		else:
			return;
	else:
		if(userNick.count('@')):
			trueJid = userNick;
		else:
			return;
	if(len(param) == 2):
		access = param[1];
		if(access.isdigit()):
			setPermGlobalAccess(trueJid, int(access));
			sendMsg(type, conference, nick, u'дала');
		else:
			sendMsg(type, conference, nick, u'ошибочный запрос');
	else:
		setPermGlobalAccess(trueJid);
		sendMsg(type, conference, nick, u'сняла');

registerCommand(setGlobalAccess, u'глобдоступ', 100, u'Устанавливает или снимает (если не писать уровень) уровень доступа для определённого пользователя на определённый уровень глобально', u'глобдоступ <ник> [уровень]', (u'глобдоступ guy', u'глобдоступ Nick 100'), CHAT | FROZEN | PARAM);

def showGlobalAccesses(type, conference, nick, param):
	if(not gGlobalAccess):
		sendMsg(type, conference, nick, u'нет глобальных доступов');
	else:
		items = [u'%s [%d]' % (jid, gGlobalAccess[jid]) for jid in gGlobalAccess];
		sendMsg(type, conference, nick, u'вот, что я нашла\n' + '\n'.join(items));

registerCommand(showGlobalAccesses, u'доступы', 100, u'Показывает все глобальные доступы', None, (u'доступы', ), ANY | NONPARAM);

def showLocalAccesses(type, conference, nick, param):
	if(not gPermAccess[conference]):
		sendMsg(type, conference, nick, u'нет локальных доступов');
	else:
		items = [u'\n%s [%d]' % (jid, gPermAccess[conference][jid]) for jid in gPermAccess[conference]];
		sendMsg(type, conference, nick, u'вот, что я нашла\n' + '\n'.join(items));

registerCommand(showLocalAccesses, u'локалдоступы', 20, u'Показывает все локальные доступы', None, (u'локалдоступы', ), CHAT | NONPARAM);

def loadGlobalAccesses():
	global gGlobalAccess;
	createFile(GLOBACCESS_FILE, '{}');
	gGlobalAccess = eval(readFile(GLOBACCESS_FILE));
	for jid in gAdmins:
		gGlobalAccess[jid] = 100;

registerEvent(loadGlobalAccesses, STARTUP);

def loadLocalAccesses(conference):
	fileName = PERMACCESS_FILE % (conference);
	createFile(fileName, '{}');
	gPermAccess[conference] = eval(readFile(fileName));
	gTempAccess[conference] = {};

registerEvent(loadLocalAccesses, ADDCONF);

def unloadLocalAccesses(conference):
	del(gPermAccess[conference]);
	del(gTempAccess[conference]);

registerEvent(unloadLocalAccesses, DELCONF);
