# coding: utf-8;

# record.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

REC_FILE = 'config/%s/record.txt';
gRecordsCache = {};

def showRecord(type, conference, nick, param):
	if(not gRecordsCache[conference]):
		sendMsg(type, conference, nick, u'нет информации');
	else:
		sendMsg(type, conference, nick, u'рекорд посещаемости - %(count)d человек (%(time)s)' % (gRecordsCache[conference]));

registerCommand(showRecord, u'рекорд', 10, u'Показывает рекорд посещаемости конференции', None, (u'рекорд', ), CHAT | NONPARAM);

def calculateRecord(conference, nick, trueJid, aff, role):
	userCount = len(getJidList(conference))
	lastCount = gRecordsCache[conference] and gRecordsCache[conference]['count'] or 0;
	if(userCount >= lastCount):
		gRecordsCache[conference]['time'] = time.strftime('%d.%m.%y, %H:%M');
		gRecordsCache[conference]['count'] = userCount;
		writeFile(REC_FILE % (conference), str(gRecordsCache[conference]));

registerJoinHandler(calculateRecord);

def loadRecordCache(conference):
	fileName = REC_FILE % (conference);
	createFile(fileName, '{}');
	gRecordsCache[conference] = eval(readFile(fileName));

registerEvent(loadRecordCache, ADDCONF);

def unloadRecordCache(conference):
	del(gRecordsCache[conference]);

registerEvent(unloadRecordCache, DELCONF);
