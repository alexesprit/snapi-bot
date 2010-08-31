# coding: utf-8;

# seen.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

SEEN_FILE = 'config/%s/seen.txt';

gSeen = {};

def showSeenTime(type, conference, nick, param):
	userNick = param or nick;
	if(nickInConference(conference, userNick)):
		trueJid = getTrueJid(conference, userNick);
		seenTime = gSeen[conference].getKey(trueJid);
		if(seenTime):
			seenDate = time.strftime('%H:%M, %d.%m.%Y', time.localtime(seenTime));
			seenTime = time2str(time.time() - seenTime);
			if(not param):
				sendMsg(type, conference, nick, u'я видела тебя %s назад (в %s)' % (seenTime, seenDate));
			else:
				sendMsg(type, conference, nick, u'я видела %s %s назад (в %s)' % (userNick, seenTime, seenDate));
		else:
			sendMsg(type, conference, nick, u'нет информации');
	else:
		sendMsg(type, conference, nick, u'а это кто?');

registerCommand(showSeenTime, u'когдабыл', 10, u'Показывает, сколько времени назад пользователь вышел из чата', u'когдабыл [ник]', (u'когдабыл Nick', ), CHAT);

def updateSeenTime(conference, nick, trueJid, reason, code):
	if('303' != code):
		gSeen[conference].setKey(trueJid, time.time());
		gSeen[conference].save();

registerLeaveHandler(updateSeenTime);

def loadSeenBase(conference):
	fileName = SEEN_FILE % (conference);
	createFile(fileName, '{}');
	gSeen[conference] = database.DataBase(fileName);

registerEvent(loadSeenBase, ADDCONF);
