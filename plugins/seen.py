# coding: utf-8

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

SEEN_FILE = "seen.txt"

gSeenCache = {}

def loadSeenBase(conference):
	fileName = getConfigPath(conference, SEEN_FILE)
	gSeenCache[conference] = database.DataBase(fileName)

def freeSeenBase(conference):
	del(gSeenCache[conference])

def updateSeenTime(conference, nick, trueJid, reason, code):
	if("303" != code):
		gSeenCache[conference][trueJid] = time.time()
		gSeenCache[conference].save()

def showSeenTime(msgType, conference, nick, param):
	userNick = param or nick
	if(nickInConference(conference, userNick)):
		trueJid = getTrueJid(conference, userNick)
		if(trueJid in gSeenCache[conference]):
			seen = gSeenCache[conference][trueJid]
			seenDate = time.strftime("%H:%M, %d.%m.%Y", time.localtime(seen))
			seenTime = time2str(time.time() - seen)
			if(not param):
				sendMsg(msgType, conference, nick, u"последний раз я видела тебя %s назад (в %s)" % (seenTime, seenDate))
			else:
				sendMsg(msgType, conference, nick, u"последний раз я видела %s %s назад (в %s)" % (userNick, seenTime, seenDate))
		else:
			sendMsg(msgType, conference, nick, u"нет информации")
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")

registerLeaveHandler(updateSeenTime)

registerEvent(loadSeenBase, ADDCONF)
registerEvent(freeSeenBase, DELCONF)

registerCommand(showSeenTime, u"когдабыл", 10, 
				u"Показывает, сколько времени назад пользователь вышел из чата", 
				u"когдабыл [ник]", 
				(u"когдабыл Nick", ), 
				CHAT)
