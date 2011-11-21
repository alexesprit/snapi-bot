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

def loadAutoModerators(conference):
	path = getConfigPath(conference, MODERATORS_FILE)
	gModerators[conference] = eval(utils.readFile(path, "[]"))

def freeAutoModerators(conference):
	del gModerators[conference]

def saveAutoModerators(conference):
	path = getConfigPath(conference, MODERATORS_FILE)
	utils.writeFile(path, str(gModerators[conference]))

def setAutoModerator(conference, nick, truejid, aff, role):
	if truejid in gModerators[conference]:
		setMUCRole(conference, nick, protocol.ROLE_MODERATOR, u"Автомодератор")

def addAutoModerator(msgType, conference, nick, param):
	user = param
	setModeratorRole = False
	if isNickInConference(conference, user):
		truejid = getTrueJID(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setModeratorRole = True
	elif isJID(user):
		truejid = user
		user = getNickByJID(conference, truejid)
		if user:
			setModeratorRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	if truejid not in gModerators[conference]:
		gModerators[conference].append(truejid)
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
		truejid = getTrueJID(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setParticipantRole = True
	elif isJID(user):
		truejid = user
		user = getNickByJID(conference, truejid)
		if user:
			setParticipantRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	if truejid in gModerators[conference]:
		gModerators[conference].remove(truejid)
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
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Отправила в приват")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
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
