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

TALKERS_FILE = "talkers.dat"

gTalkersCache = {}

def loadTalkersBase(conference):
	path = getConfigPath(conference, TALKERS_FILE)
	gTalkersCache[conference] = database.DataBase(path)

def freeTalkersBase(conference):
	gTalkersCache[conference].save()
	del gTalkersCache[conference]

def saveAllTalkersBases():
	for conference in getConferences():
		gTalkersCache[conference].save()

def updateTalkersInfo(stanza, msgType, conference, nick, truejid, body):
	if msgType == protocol.TYPE_PUBLIC:
		if truejid != Config.JID and truejid != conference:
			base = gTalkersCache[conference]
			if truejid in base:
				base[truejid]["nick"] = nick
			else:
				base[truejid] = {"nick": nick, "words": 0, "messages": 0, "mes": 0}
			if body.startswith("/me"):
				base[truejid]["mes"] += 1
			else:
				base[truejid]["messages"] += 1
			base[truejid]["words"] += len(body.split())

def showTalkerInfo(msgType, conference, nick, param):
	if param == u"топ":
		base = gTalkersCache[conference]
		if base:
			topList = []
			pattern = u"%d) %s, %d, %d, %d, %0.1f"
			for info in base.values():
				words = info["words"]
				userNick = info["nick"]
				messages = info["messages"]
				meMessages = info["mes"]
				wordsPerMsg = (float(words)) / (messages + meMessages)
				topList.append([messages, meMessages, words, wordsPerMsg, userNick])
			topList.sort()
			topList.reverse()
			topList = topList[:10]
			elements = [pattern % (i + 1, element[4], element[0], element[1], element[2], element[3])
						for i, element in enumerate(topList)]
			sendMsg(msgType, conference, nick,
				u"Список топ-участников\nНик, сообщ., /me, слов, слов на сообщ.\n%s" % ("\n".join(elements)))
		else:
			sendMsg(msgType, conference, nick, u"База болтунов пуста")
	elif param == u"сброс":
		conference = source[1]
		truejid = getTrueJID(conference, nick)
		if getAccess(conference, truejid) >= 20:
			base = gTalkersCache[conference]
			base.clear()
			base.save()
			sendMsg(msgType, conference, nick, u"База данных очищена")
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		userNick = param or nick
		truejid = getTrueJID(conference, userNick)
		if not truejid:
			if netutil.isJID(userNick):
				truejid = userNick
			else:
				sendMsg(msgType, conference, nick, u"А это кто?")
				return
		if truejid in gTalkersCache[conference]:
			statistic = gTalkersCache[conference][truejid]
			userNick = statistic["nick"]
			words = statistic["words"]
			messages = statistic["messages"]
			meMessages = statistic["mes"]
			wordsPerMsg = (float(words)) / (messages + meMessages)
			sendMsg(msgType, conference, nick,
				u"Статистика для %s\nСообщ.: %d\n/me: %d\nСлов: %d\nСлов на сообщ.: %0.1f" %
					(userNick, messages, meMessages, words, wordsPerMsg))
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")

registerEventHandler(loadTalkersBase, EVT_ADDCONFERENCE)
registerEventHandler(freeTalkersBase, EVT_DELCONFERENCE)

registerEventHandler(saveAllTalkersBases, EVT_SHUTDOWN)

registerEventHandler(updateTalkersInfo, EVT_MSG | H_CONFERENCE)

registerCommand(showTalkerInfo, u"болтун", 10,
				u"Показывает статистику болтливости указанного пользователя. Параметр \"топ\" - список десяти самых болтливых. Параметр \"сброс\" - очистка статистики",
				u"[ник]",
				(None, u"топ", u"Nick"),
				CMD_CONFERENCE)
