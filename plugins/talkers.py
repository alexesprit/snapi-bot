# coding: utf-8

# talkers.py
# Initial Copyright (c) Gigabyte
# Modification Copyright (c) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

SAVE_COUNT = 20
TALKERS_FILE = "talkers.txt"

gTalkersCache = {}

def showTopTalkersInfo(msgType, conference, nick):
	base = gTalkersCache[conference]
	if base.isEmpty():
		sendMsg(msgType, conference, nick, u"База болтунов пуста")
	else:
		topList = []
		replic = u"Статистика топ-участников\nНик, сообщ., /me, слов, слов на сообщ.\n"
		topListLine = u"%d) %s, %d, %d, %d, %0.1f"
		count = 10
		for jid, info in base.items():
			words = info["words"]
			userNick = info["nick"]
			messages = info["messages"]
			meMessages = info["mes"]
			wordsPerMsg = (float(words)) / (messages + meMessages)
			topList.append([messages, meMessages, words, wordsPerMsg, userNick])
		topList.sort()
		topList.reverse()
		topList = topList[:10]
		items = [topListLine % (i + 1, x[4], x[0], x[1], x[2], x[3]) for i, x in enumerate(topList)]
		sendMsg(msgType, conference, nick, replic + "\n".join(items))

def clearTalkersInfo(msgType, conference, nick):
	conference = source[1]
	trueJid = getTrueJid(conference, nick)
	if getAccess(conference, trueJid) >= 20:
		base = gTalkersCache[conference]
		base.clear()
		base.save()
		sendMsg(msgType, conference, nick, u"База данных очищена")
	else:
		sendMsg(msgType, conference, nick, u"Недостаточно прав")

def showTalkerInfo(msgType, conference, nick, param):
	if param == u"топ":
		showTopTalkersInfo(msgType, conference, nick)
	elif param == u"сброс":
		clearTalkersInfo(msgType, conference, nick)
	else:
		if not param:
			trueJid = getTrueJid(conference, nick)
		elif isNickInConference(conference, param):
			trueJid = getTrueJid(conference, param)
		else:
			return
		base = gTalkersCache[conference]
		if trueJid in base:
			statistic = base[trueJid]
			statisticLine = u"Статистика для %s\nСообщ.: %d\n/me: %d\nСлов: %d\nСлов на сообщ.: %0.1f"
			nick = statistic["nick"]
			words = statistic["words"]
			messages = statistic["messages"]
			meMessages = statistic["mes"]
			wordsPerMsg = (float(words)) / (messages + meMessages)
			message = statisticLine % (nick, messages, meMessages, words, wordsPerMsg)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")

def updateTalkersInfo(stanza, msgType, conference, nick, trueJid, body):
	if msgType == protocol.TYPE_PUBLIC:
		if trueJid != PROFILE_JID and trueJid != conference:
			base = gTalkersCache[conference]
			if trueJid in base:
				base[trueJid]["nick"] = nick
			else:
				base[trueJid] = {"nick": nick, "words": 0, "messages": 0, "mes": 0}
			if body.startswith("/me"):
				base[trueJid]["mes"] += 1
			else:
				base[trueJid]["messages"] += 1
			base[trueJid]["words"] += len(body.split())

def loadTalkersBase(conference):
	path = getConfigPath(conference, TALKERS_FILE)
	gTalkersCache[conference] = database.DataBase(path)

def freeTalkersBase(conference):
	del gTalkersCache[conference]

def saveAllTalkersBases():
	for conference in getConferences():
		gTalkersCache[conference].save()

registerEvent(loadTalkersBase, EVT_ADDCONFERENCE)
registerEvent(freeTalkersBase, EVT_DELCONFERENCE)
registerEvent(saveAllTalkersBases, EVT_SHUTDOWN)

registerMessageHandler(updateTalkersInfo, H_CONFERENCE)

registerCommand(showTalkerInfo, u"болтун", 10, 
				u"Показывает статистику болтливости указанного пользователя. Параметр \"топ\" - список десяти самых болтливых. Параметр \"сброс\" - очистка статистики", 
				u"[ник]", 
				(None, u"топ", u"Nick"), 
				CMD_CONFERENCE)
