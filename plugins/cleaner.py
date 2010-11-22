# coding: utf-8

# cleaner.py
# Removing bases from old keys
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CLEAN_TIMEOUT = 86400
CHAT_KEEP_TIME = 86400 * 90
SINGLE_KEEP_TIME = 86400 * 120
LOGS_KEEP_TIME = 86400 * 10

CHAT_BASES = (
		"gUserClients", 
		"gTalkersCache", 
		"gQuizScores", 
		"gHereTime", 
		"gSendCache", 
		"gSeenCache"
)
SINGLE_BASES = ("gUserNotes", )

def cleanBase(base, keepTime):
	bGetUpdateTime = base.getChangeTime
	cleanedKeys = 0
	for key in base.keys():
		updateTime = bGetUpdateTime(key)
		if time.time() - updateTime >= keepTime:
			del base[key]
			cleanedKeys += 1
	if cleanedKeys:
		base.save()
	return cleanedKeys

def cleanBases():
	_cleanBase = cleanBase
	for conference in getConferences():
		cleanedKeys = 0
		for item in CHAT_BASES:
			base = globals()[item][conference]
			cleanedKeys += _cleanBase(base, CHAT_KEEP_TIME)
		if cleanedKeys:
			printf(u"%d keys were removed from %s bases" % (cleanedKeys, conference))
	for item in SINGLE_BASES:
		cleanedKeys = 0
		base = globals()[item]
		_cleanBase(base, SINGLE_KEEP_TIME)
		if cleanedKeys:
			printf(u"%d keys were removed from %s base" % (cleanedKeys, item))
	for log in os.listdir(SYSLOG_DIR):
		path = os.path.join(SYSLOG_DIR, log)
		if os.path.isfile(path):
			changeTime = os.path.getctime(path)
			if time.time() - changeTime > LOGS_KEEP_TIME:
				os.remove(path)
	startCleanTimer()

def startCleanTimer():
	startTimer(CLEAN_TIMEOUT, cleanBases)

registerEvent(startCleanTimer, EVT_INIT_2)
