# coding: utf-8;

# moderators.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

MODERATORS_FILE = 'moderators.txt';

gModerators = {};

def saveAutoModerators(conference):
	fileName = getConfigPath(conference, MODERATORS_FILE);
	writeFile(fileName, str(gModerators[conference]));

def loadAutoModerators(conference):
	fileName = getConfigPath(conference, MODERATORS_FILE);
	createFile(fileName, '[]');
	gModerators[conference] = eval(readFile(fileName));

registerEvent(loadAutoModerators, ADDCONF);

def unloadAutoModerators(conference):
	del(gModerators[conference]);

registerEvent(unloadAutoModerators, DELCONF);

def setAutoModerator(conference, nick, trueJid, aff, role):
	if(trueJid in gModerators[conference]):
		setRole(conference, nick, ROLE_MODERATOR, u'автомодератор');

registerJoinHandler(setAutoModerator);

def addAutoModerator(msgType, conference, nick, param):
	user = param;
	setModeratorRole = False;
	if(nickInConference(conference, user)):
		trueJid = getTrueJid(conference, user);
		if(getNickKey(conference, user, NICK_HERE)):
			setModeratorRole = True;
	elif(param.count('@')):
		trueJid = user;
		user = getNickByJid(conference, trueJid);
		if(user):
			setModeratorRole = True;
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
		return;
	if(trueJid not in gModerators[conference]):
		gModerators[conference].append(trueJid);
		saveAutoModerators(conference);
		sendMsg(msgType, conference, nick, u'добавила');
		if(setModeratorRole):
			setRole(conference, user, ROLE_MODERATOR);
	else:
		sendMsg(msgType, conference, nick, u'%s уже есть в списке' % (param));

registerCommand(addAutoModerator, u'модер+', 20, u'Добавляет ник или жид в список автомодераторов', u'модер+ <ник/жид>', (u'модер+ Nick', u'модер+ nick@jabber.ru'), CHAT | PARAM);

def delAutoModerator(msgType, conference, nick, param):
	user = param;
	setParticipantRole = False;
	if(nickInConference(conference, user)):
		trueJid = getTrueJid(conference, user);
		if(getNickKey(conference, user, NICK_HERE)):
			setParticipantRole = True;
	elif(param.count('@')):
		trueJid = user;
		user = getNickByJid(conference, trueJid);
		if(user):
			setParticipantRole = True;
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
		return;
	if(trueJid in gModerators[conference]):
		gModerators[conference].remove(trueJid);
		saveAutoModerators(conference);
		sendMsg(msgType, conference, nick, u'удалила');
		if(setParticipantRole):
			setRole(conference, user, ROLE_PARTICIPANT);
	else:
		sendMsg(msgType, conference, nick, u'а %s итак нет в списке' % (param));

registerCommand(delAutoModerator, u'модер-', 20, u'Удаляет ник или жид из списка автомодераторов', u'модер- <ник/жид>', (u'модер- Nick', u'модер- nick@jabber.ru'), CHAT | PARAM);

def showAutoModerators(msgType, conference, nick, param):
	if(gModerators[conference]):
		items = [u'%d) %s' % (i + 1, moder) for i, moder in enumerate(gModerators[conference])];
		message = u'список автомодераторов:\n%s' % ('\n'.join(items));
		sendMsg(msgType, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u'список автомодераторов пуст');

registerCommand(showAutoModerators, u'модер*', 20, u'Показывает список автомодераторов', None, (u'модер*', ), CHAT | NONPARAM);
