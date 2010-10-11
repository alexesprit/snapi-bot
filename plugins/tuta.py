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

def showHereStatistic(msgType, conference, nick, param):
	userNick = param or nick
	if(nickIsOnline(conference, userNick)):
		base = gHereTime[conference]
		trueJid = getTrueJid(conference, userNick)
		if(trueJid in base):
			joinCount = base[trueJid]["count"]
			hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)
			totalTime = base[trueJid]["here"] + hereTime
			averageTime = totalTime / joinCount
			record = max(base[trueJid]["record"], hereTime)
			message = param and userNick or u"ты"
			message = u"%s всего здесь %s, рекорд - %s, среднее время - %s, заходов в чат - %d" % (message, time2str(totalTime), time2str(record), time2str(averageTime), joinCount)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"нет информации")
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")
	
def updateJoinStatistic(conference, nick, trueJid, aff, role):
	base = gHereTime[conference]
	if(trueJid not in base):
		base[trueJid] = {"record": 0, "count": 0, "here": 0}
	base[trueJid]["count"] += 1
	base.save()

def updateLeaveStatistic(conference, nick, trueJid, reason, code):
	base = gHereTime[conference]
	joinTime = getNickKey(conference, nick, "joined")
	if(trueJid in base):
		hereTime = time.time() - getNickKey(conference, nick, NICK_JOINED)
		base[trueJid]["here"] += hereTime
		base[trueJid]["record"] = max(base[trueJid]["record"], hereTime)
		base.save()

def loadHereBase(conference):
	fileName = getConfigPath(conference, HERE_FILE)
	gHereTime[conference] = database.DataBase(fileName)

def freeHereBase(conference):
	del(gHereTime[conference])

def saveAllHereBases():
	for conference in getConferences():
		gHereTime[conference].save()

registerEvent(loadHereBase, ADDCONF)
registerEvent(freeHereBase, DELCONF)
registerEvent(saveAllHereBases, SHUTDOWN)

registerJoinHandler(updateJoinStatistic)
registerLeaveHandler(updateLeaveStatistic)

registerCommand(showHereStatistic, u"тута", 10, 
				u"Показывает кол-во часов, проведённое в чатике, максимальное и среднее", 
				u"тута [ник]", 
				(u"тута", ), 
				CHAT);
