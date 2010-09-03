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

def saveModerators(conference):
	fileName = getConfigPath(conference, MODERATORS_FILE);
	writeFile(fileName, str(gModerators[conference]));

def loadModerators(conference):
	fileName = getConfigPath(conference, MODERATORS_FILE);
	createFile(fileName, '[]');
	gModerators[conference] = eval(readFile(fileName));

registerEvent(loadModerators, ADDCONF);

def setModerator(conference, nick, trueJid, aff, role):
	if(trueJid in gModerators[conference]):
		setRole(conference, nick, ROLE_MODERATOR, u'автомодератор');

registerJoinHandler(setModerator);

def addModerator(msgType, conference, nick, param):
	if(nickInConference(conference, param)):
		trueJid = getTrueJid(conference, param);
	elif(param.count('@')):
		trueJid = param;
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
		return;
	gModerators[conference].append(trueJid);
	saveModerators(conference);
	sendMsg(msgType, conference, nick, u'добавила');

registerCommand(addModerator, u'модер+', 20, u'Добавляет ник или жид в список автомодераторов', u'модер+ <ник/жид>', (u'модер+ Nick', u'модер+ nick@jabber.ru'), CHAT | PARAM);

def delModerator(msgType, conference, nick, param):
	if(nickInConference(conference, param)):
		trueJid = getTrueJid(conference, param);
	elif(param.count('@')):
		trueJid = param;
	else:
		sendMsg(msgType, conference, nick, u'а это кто?');
		return;
	if(trueJid in gModerators[conference]):
		gModerators[conference].remove(trueJid);
		saveModerators(conference);
		sendMsg(msgType, conference, nick, u'удалила');
	else:
		sendMsg(msgType, conference, nick, u'а %s итак нет в списке' % (param));

registerCommand(delModerator, u'модер-', 20, u'Удаляет ник или жид из списка автомодераторов', u'модер- <ник/жид>', (u'модер- Nick', u'модер- nick@jabber.ru'), CHAT | PARAM);

def showModerator(msgType, conference, nick, param):
	if(gModerators[conference]):
		items = [u'%d) %s' % (i + 1, moder) for i, moder in enumerate(gModerators[conference])];
		message = u'список автомодераторов:\n%s' % ('\n'.join(items));
		sendMsg(msgType, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u'список автомодераторов пуст');

registerCommand(showModerator, u'модер*', 20, u'Показывает список автомодераторов', None, (u'модер*', ), CHAT | NONPARAM);
