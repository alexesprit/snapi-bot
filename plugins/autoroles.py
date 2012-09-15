# coding: utf-8

# autoroles.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

AUTOROLES_FILE = "autoroles.dat"

def openAutoRolesBase(conference):
	path = getConfigPath(conference, AUTOROLES_FILE)
	return io.load(path, {})

def saveAutoRolesBase(conference, roles):
	path = getConfigPath(conference, AUTOROLES_FILE)
	io.dump(path, roles)

def setAutoRole(conference, nick, truejid, aff, role):
	roles = openAutoRolesBase(conference)
	if truejid in roles:
		newrole = roles[truejid]
		reason = (newrole == "moder") and u"Автомодератор" or u"Автопосетитель"
		setMUCRole(conference, nick, newrole, reason)

def addAutoRole(msgType, conference, nick, param, role):
	user = param
	setNewRole = False
	if isNickInConference(conference, user):
		truejid = getTrueJID(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setNewRole = True
	elif netutil.isJID(user):
		truejid = user
		user = getNickByJID(conference, truejid)
		if user:
			setNewRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	roles = openAutoRolesBase(conference)
	if truejid in roles:
		oldrole = roles[truejid]
		if oldrole == role:
			sendMsg(msgType, conference, nick, u"%s уже есть в списке!" % (param))
			return
	roles[truejid] = role
	saveAutoRolesBase(conference, roles)
	sendMsg(msgType, conference, nick, u"Добавила")
	if setNewRole:
		setMUCRole(conference, user, role)

def delAutoRole(msgType, conference, nick, param):
	user = param
	setNewRole = False
	if isNickInConference(conference, user):
		truejid = getTrueJID(conference, user)
		if getNickKey(conference, user, NICK_HERE):
			setNewRole = True
	elif netutil.isJID(user):
		truejid = user
		user = getNickByJID(conference, truejid)
		if user:
			setNewRole = True
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")
		return
	roles = openAutoRolesBase(conference)
	if truejid in roles:
		del roles[truejid]
		saveAutoRolesBase(conference, roles)
		sendMsg(msgType, conference, nick, u"Удалила")
		if setNewRole:
			setMUCRole(conference, user, protocol.ROLE_PARTICIPANT)
	else:
		sendMsg(msgType, conference, nick, u"А %s итак нет в списке" % (param))

def showAutoRoles(msgType, conference, nick, param, role):
	roles = openAutoRolesBase(conference)
	elements = [u"%d) %s" % (i + 1, truejid)
				for i, truejid in enumerate(sorted(roles)) if roles[truejid] == role]
	if elements:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Отправила в приват")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, "\n".join(elements))
	else:
		sendMsg(msgType, conference, nick, u"Cписок пуст")

def addAutoVisitor(msgType, conference, nick, param):
	addAutoRole(msgType, conference, nick, param, "visitor")

def addAutoModerator(msgType, conference, nick, param):
	addAutoRole(msgType, conference, nick, param, "moder")
	
def showAutoVisitors(msgType, conference, nick, param):
	showAutoRoles(msgType, conference, nick, param, "visitor")
	
def showAutoModerators(msgType, conference, nick, param):
	showAutoRoles(msgType, conference, nick, param, "moder")

registerEventHandler(setAutoRole, EVT_USERJOIN)

registerCommand(addAutoVisitor, u"девойс+", 15,
				u"Добавляет пользователя в список автопосетителей",
				u"<ник|жид>",
				(u"Nick", u"user@server.tld"),
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(addAutoModerator, u"модер+", 20,
				u"Добавляет пользователя в список автомодераторов",
				u"<ник|жид>",
				(u"Nick", u"nick@server.tld"),
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delAutoRole, u"модер-", 20,
				u"Удаляет пользователя из списка автомодераторов",
				u"<ник|жид>",
				(u"Nick", u"nick@server.tld"),
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delAutoRole, u"девойс-", 15,
				u"Удаляет пользователя из списка автопосетителей",
				u"<ник|жид>",
				(u"Nick", u"user@server.tld"),
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showAutoModerators, u"модер*", 20,
				u"Показывает список автомодераторов",
				None,
				None,
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showAutoVisitors, u"девойс*", 15,
				u"Показывает список автопосетителей",
				None,
				None,
				CMD_CONFERENCE | CMD_NONPARAM)