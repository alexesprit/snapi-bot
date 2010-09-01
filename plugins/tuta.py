# coding: utf-8;

# tuta.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

HERE_FILE = 'config/%s/tuta.txt';

gHereTime = {};

def showHereStatistic(type, conference, nick, param):
	userNick = param or nick;
	if(nickIsOnline(conference, userNick)):
		base = gHereTime[conference];
		trueJid = getTrueJid(conference, userNick);
		info = base.getKey(trueJid);
		if(info):
			joinCount = info['count'];
			hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED);
			totalTime = info['here'] + hereTime;
			averageTime = totalTime / joinCount;
			record = max(info['record'], hereTime);
			message = param and userNick or u'ты';
			message = u'%s всего здесь %s, рекорд - %s, среднее время - %s, заходов в чат - %d' % (message, time2str(totalTime), time2str(record), time2str(averageTime), joinCount);
			sendMsg(type, conference, nick, message);
		else:
			sendMsg(type, conference, nick, u'нет информации');
	else:
		sendMsg(type, conference, nick, u'а это кто?');

registerCommand(showHereStatistic, u'тута', 10, u'Показывает кол-во часов, проведённое в чатике, максимальное и среднее', u'тута [ник]', (u'тута', ), CHAT);
	
def updateJoinStatistic(conference, nick, trueJid, aff, role):
	base = gHereTime[conference];
	info = base.getKey(trueJid);
	if(not info):
		info = {'record': 0, 'count': 0, 'here': 0};
	info['count'] += 1;
	base.setKey(trueJid, info);
	base.save();

registerJoinHandler(updateJoinStatistic);

def updateLeaveStatistic(conference, nick, trueJid, reason, code):
	base = gHereTime[conference];
	joinTime = getNickKey(conference, nick, 'joined');
	if(joinTime):
		info = base.getKey(trueJid);
		if(info):
			hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED);
			info['here'] += hereTime;
			info['record'] = max(info['record'], hereTime);
			base.setKey(trueJid, info);
			base.save();

registerLeaveHandler(updateLeaveStatistic);

def loadHereCache(conference):
	fileName = HERE_FILE % (conference);
	gHereTime[conference] = database.DataBase(fileName);

registerEvent(loadHereCache, ADDCONF);

def unloadHereCache(conference):
	del(gHereTime[conference]);

registerEvent(unloadHereCache, DELCONF);