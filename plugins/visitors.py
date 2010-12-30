# coding: utf-8

# visitors.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VISITORS_FILE = "visitors.txt"

gVisitors = {}

def saveAutoVisitors(conference):
	path = getConfigPath(conference, VISITORS_FILE)
	utils.writeFile(path, str(gVisitors[conference]))

def loadAutoVisitors(conference):
	path = getConfigPath(conference, VISITORS_FILE)
	utils.createFile(path, "[]")
	gVisitors[conference] = eval(utils.readFile(path))

def freeAutoVisitors(conference):
	del gVisitors[conference]

def setAutoVisitor(conference, nick, truejid, aff, role):
	if truejid in gVisitors[conference]:
		setMUCRole(conference, nick, protocol.ROLE_VISITOR, u"Автопосетитель")

def addAutoVisitor(msgType, conference, nick, param):
	user = param
	setVisitorRole = False
	if isNickInConference(conference, user):
		truejid = getTrueJID(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setVisitorRole = True
	elif isJID(user):
		truejid = user
		user = getNickByJID(conference, truejid)
		if user:
			setVisitorRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	if truejid not in gVisitors[conference]:
		gVisitors[conference].append(truejid)
		saveAutoVisitors(conference)
		sendMsg(msgType, conference, nick, u"Добавила")
		if setVisitorRole:
			setMUCRole(conference, user, protocol.ROLE_VISITOR)
	else:
		sendMsg(msgType, conference, nick, u"%s уже есть в списке!" % (param))

def delAutoVisitort(msgType, conference, nick, param):
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
	if truejid in gVisitors[conference]:
		gVisitors[conference].remove(truejid)
		saveAutoVisitors(conference)
		sendMsg(msgType, conference, nick, u"Удалила")
		if setParticipantRole:
			setMUCRole(conference, user, protocol.ROLE_PARTICIPANT)
	else:
		sendMsg(msgType, conference, nick, u"А %s итак нет в списке" % (param))

def showAutoVisitors(msgType, conference, nick, param):
	if gVisitors[conference]:
		elements = [u"%d) %s" % (i + 1, moder) 
				for i, moder in enumerate(sorted(gVisitors[conference]))]
		message = u"Список автомодераторов:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"список автопосетителей пуст")

registerEventHandler(loadAutoVisitors, EVT_ADDCONFERENCE)
registerEventHandler(freeAutoVisitors, EVT_DELCONFERENCE)

registerEventHandler(setAutoVisitor, EVT_USERJOIN)

registerCommand(addAutoVisitor, u"девойс+", 15, 
				u"Добавляет пользователя в список автопосетителей", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delAutoVisitort, u"девойс-", 15, 
				u"Удаляет пользователя из списка автопосетителей", 
				u"<ник|жид>", 
				(u"Nick", u"user@server.tld"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showAutoVisitors, u"девойс*", 15, 
				u"Показывает список автопосетителей", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
