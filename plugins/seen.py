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
	path = getConfigPath(conference, SEEN_FILE)
	gSeenCache[conference] = database.DataBase(path)

def freeSeenBase(conference):
	del gSeenCache[conference]

def saveAllSeenBases():
	for conference in getConferences():
		gSeenCache[conference].save()

def updateSeenTime(conference, nick, truejid, reason, code):
	if "303" != code:
		gSeenCache[conference][truejid] = time.time()

def showSeenTime(msgType, conference, nick, param):
	userNick = param or nick
	if isNickInConference(conference, userNick):
		truejid = getTrueJID(conference, userNick)
		if truejid in gSeenCache[conference]:
			rawtime = gSeenCache[conference][truejid]
			seenDate = time.strftime("%H:%M, %d.%m.%Y", time.localtime(rawtime))
			seenTime = getTimeStr(time.time() - rawtime)
			if not param:
				message = u"Последний раз я видела тебя %s назад (в %s)" % (seenTime, seenDate)
			else:
				message = u"Последний раз я видела %s %s назад (в %s)" % (userNick, seenTime, seenDate)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

registerEventHandler(updateSeenTime, EVT_USERLEAVE)

registerEventHandler(loadSeenBase, EVT_ADDCONFERENCE)
registerEventHandler(freeSeenBase, EVT_DELCONFERENCE)

registerEventHandler(saveAllSeenBases, EVT_SHUTDOWN)

registerCommand(showSeenTime, u"когдабыл", 10, 
				u"Показывает, сколько времени назад пользователь вышел из чата", 
				u"[ник]", 
				(u"Nick", ), 
				CMD_CONFERENCE)
