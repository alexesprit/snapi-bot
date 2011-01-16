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

def loadHereBase(conference):
	path = getConfigPath(conference, HERE_FILE)
	gHereTime[conference] = database.DataBase(path)

def freeHereBase(conference):
	del gHereTime[conference]

def saveAllHereBases():
	for conference in getConferences():
		for nick in getOnlineNicks(conference):
			truejid = getTrueJID(conference, nick)
			updateHereTimeInfo(conference, nick, truejid)
		gHereTime[conference].save()

def showHereStatistic(msgType, conference, nick, param):
	userNick = param or nick
	if isNickOnline(conference, userNick):
		base = gHereTime[conference]
		truejid = getTrueJID(conference, userNick)
		if truejid in base:
			joinCount = base[truejid]["count"]
			hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)

			totalTime = base[truejid]["here"] + hereTime
			maxTime = max(base[truejid]["record"], hereTime)
			averageTime = totalTime / joinCount

			if not param:
				sendMsg(msgType, conference, nick, 
					u"Ты всего здесь %s, рекорд - %s, среднее время - %s, заходов в чат - %d" % 
						(getTimeStr(totalTime), getTimeStr(maxTime), getTimeStr(averageTime), joinCount))
			else:
				sendMsg(msgType, conference, nick, 
					u"%s всего здесь %s, рекорд - %s, среднее время - %s, заходов в чат - %d" % 
						(userNick, getTimeStr(totalTime), getTimeStr(maxTime), getTimeStr(averageTime), joinCount))
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

def updateHereTimeInfo(conference, nick, truejid):
	base = gHereTime[conference]
	if truejid in base:
		hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)
		base[truejid]["here"] += hereTime
		base[truejid]["record"] = max(base[truejid]["record"], hereTime)
		
def updateJoinStatistic(conference, nick, truejid, aff, role):
	base = gHereTime[conference]
	if truejid not in base:
		base[truejid] = {"record": 0, "count": 0, "here": 0}
	base[truejid]["count"] += 1

def updateLeaveStatistic(conference, nick, truejid, reason, code):
	updateHereTimeInfo(conference, nick, truejid)

registerEventHandler(loadHereBase, EVT_ADDCONFERENCE)
registerEventHandler(freeHereBase, EVT_DELCONFERENCE)

registerEventHandler(saveAllHereBases, EVT_SHUTDOWN)

registerEventHandler(updateJoinStatistic, EVT_USERJOIN)
registerEventHandler(updateLeaveStatistic, EVT_USERLEAVE)

registerCommand(showHereStatistic, u"тута", 10, 
				u"Показывает общее, рекордное и среднее время, проведённое в конференции", 
				u"[ник]", 
				(None, u"Nick"), 
				CMD_CONFERENCE);
