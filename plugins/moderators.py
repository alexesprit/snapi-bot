# coding: utf-8

# moderators.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

MODERATORS_FILE = "moderators.txt"

gModerators = {}

def saveAutoModerators(conference):
	path = getConfigPath(conference, MODERATORS_FILE)
	utils.writeFile(path, str(gModerators[conference]))

def loadAutoModerators(conference):
	path = getConfigPath(conference, MODERATORS_FILE)
	utils.createFile(path, "[]")
	gModerators[conference] = eval(utils.readFile(path))

def freeAutoModerators(conference):
	del gModerators[conference]

def setAutoModerator(conference, nick, trueJid, aff, role):
	if trueJid in gModerators[conference]:
		setMUCRole(conference, nick, protocol.ROLE_MODERATOR, u"Автомодератор")

def addAutoModerator(msgType, conference, nick, param):
	user = param
	setModeratorRole = False
	if isNickInConference(conference, user):
		trueJid = getTrueJid(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setModeratorRole = True
	elif isJid(user):
		trueJid = user
		user = getNickByJid(conference, trueJid)
		if user:
			setModeratorRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	if trueJid not in gModerators[conference]:
		gModerators[conference].append(trueJid)
		saveAutoModerators(conference)
		sendMsg(msgType, conference, nick, u"Добавила")
		if setModeratorRole:
			setMUCRole(conference, user, protocol.ROLE_MODERATOR)
	else:
		sendMsg(msgType, conference, nick, u"%s уже есть в списке" % (param))

def delAutoModerator(msgType, conference, nick, param):
	user = param
	setParticipantRole = False
	if isNickInConference(conference, user):
		trueJid = getTrueJid(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setParticipantRole = True
	elif isJid(user):
		trueJid = user
		user = getNickByJid(conference, trueJid)
		if user:
			setParticipantRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	if trueJid in gModerators[conference]:
		gModerators[conference].remove(trueJid)
		saveAutoModerators(conference)
		sendMsg(msgType, conference, nick, u"Удалила")
		if setParticipantRole:
			setMUCRole(conference, user, protocol.ROLE_PARTICIPANT)
	else:
		sendMsg(msgType, conference, nick, u"А %s итак нет в списке" % (param))

def showAutoModerators(msgType, conference, nick, param):
	if gModerators[conference]:
		elements = [u"%d) %s" % (i + 1, moder) 
				for i, moder in enumerate(sorted(gModerators[conference]))]
		message = u"Список автомодераторов:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Список автомодераторов пуст")

registerEventHandler(loadAutoModerators, EVT_ADDCONFERENCE)
registerEventHandler(freeAutoModerators, EVT_DELCONFERENCE)

registerEventHandler(setAutoModerator, EVT_USERJOIN)

registerCommand(addAutoModerator, u"модер+", 20, 
				u"Добавляет пользователя в список автомодераторов", 
				u"<ник|жид>", 
				(u"Nick", u"nick@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delAutoModerator, u"модер-", 20, 
				u"Удаляет пользователя из списка автомодераторов", 
				u"<ник|жид>", 
				(u"Nick", u"nick@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showAutoModerators, u"модер*", 20, 
				u"Показывает список автомодераторов", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
