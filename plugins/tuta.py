# coding: utf-8

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

HERE_FILE = "tuta.txt"

gHereTime = {}

def updateHereTimeInfo(conference, nick, trueJid):
	base = gHereTime[conference]
	joinTime = getNickKey(conference, nick, "joined")
	if trueJid in base:
		hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)
		base[trueJid]["here"] += hereTime
		base[trueJid]["record"] = max(base[trueJid]["record"], hereTime)

def showHereStatistic(msgType, conference, nick, param):
	userNick = param or nick
	if isNickOnline(conference, userNick):
		base = gHereTime[conference]
		trueJid = getTrueJid(conference, userNick)
		if trueJid in base:
			joinCount = base[trueJid]["count"]
			hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)
			totalTime = base[trueJid]["here"] + hereTime
			averageTime = totalTime / joinCount
			record = max(base[trueJid]["record"], hereTime)
			message = param and userNick or u"Ты"
			message = u"%s всего здесь %s, рекорд - %s, среднее время - %s, заходов в чат - %d" % (message, getTimeStr(totalTime), getTimeStr(record), getTimeStr(averageTime), joinCount)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
	
def updateJoinStatistic(conference, nick, trueJid, aff, role):
	base = gHereTime[conference]
	if trueJid not in base:
		base[trueJid] = {"record": 0, "count": 0, "here": 0}
	base[trueJid]["count"] += 1

def updateLeaveStatistic(conference, nick, trueJid, reason, code):
	updateHereTimeInfo(conference, nick, trueJid)

def loadHereBase(conference):
	path = getConfigPath(conference, HERE_FILE)
	gHereTime[conference] = database.DataBase(path)

def freeHereBase(conference):
	del gHereTime[conference]

def saveAllHereBases():
	for conference in getConferences():
		for nick in getOnlineNicks(conference):
			trueJid = getTrueJid(conference, nick)
			updateHereTimeInfo(conference, nick, trueJid)
		gHereTime[conference].save()

registerEvent(loadHereBase, EVT_ADDCONFERENCE)
registerEvent(freeHereBase, EVT_DELCONFERENCE)
registerEvent(saveAllHereBases, EVT_SHUTDOWN)

registerJoinHandler(updateJoinStatistic)
registerLeaveHandler(updateLeaveStatistic)

registerCommand(showHereStatistic, u"тута", 10, 
				u"Показывает кол-во часов, проведённое в чатике, максимальное и среднее", 
				u"[ник]", 
				(None, u"Nick"), 
				CMD_CONFERENCE);
