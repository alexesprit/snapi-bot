# coding: utf-8;

# cleaner.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

'''	
	Очиcтка базы данных от старых ключей.
'''

CLEAN_TIMEOUT = 86400;
CHAT_KEEP_TIME = 86400 * 30;
SINGLE_KEEP_TIME = 86400 * 90;
LOGS_KEEP_TIME = 86400 * 10;

CHAT_BASES = ('gClientsCache', 'gTalkCache', 'gQuizScores', 'gHereTimeCache', 'gSendCache');
SINGLE_BASES = ('gNotes', );

def cleanBase(base, keepTime):
	_getUpdateTime = base.getUpdateTime;
	_delKey = base.delKey;
	for key in base.items():
		updateTime = _getUpdateTime(key);
		if(time.time() - updateTime >= keepTime):
			_delKey(key);
	base.save();

def startCleaning():
	_cleanBase = cleanBase;
	for groupChat in getChatList():
		for item in CHAT_BASES:
			base = globals()[item][groupChat];
			_cleanBase(base, CHAT_KEEP_TIME);
	for item in SINGLE_BASES:
		base = globals()[item];
		_cleanBase(base, SINGLE_KEEP_TIME);
	for log in os.listdir('syslogs'):
		logPath = os.path.join('syslogs', log);
		changeTime = os.path.getctime(logPath);
		if(time.time() - changeTime > LOGS_KEEP_TIME):
			os.remove(logPath);
	startCleanTimer();

def startCleanTimer():
	startTimer(CLEAN_TIMEOUT, startCleaning);

registerPluginHandler(startCleanTimer, INIT_2);