# coding: utf-8

# access.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

ACCESS_DESC = {
	0: u"никто",
	10: u"юзер",
	11: u"мембер",
	15: u"модер",
	16: u"модер",
	20: u"админ",
	30: u"овнер",
	100: u"админ бота",
	-100: u"игнор"
}

def loadGlobalAccesses():
	global gGlobalAccess
	path = getConfigPath(ACCESS_FILE)
	gGlobalAccess = io.load(path, {})
	for jid in Config.ADMINS:
		gGlobalAccess[jid] = 100

def loadLocalAccesses(conference):
	path = getConfigPath(conference, ACCESS_FILE)
	gPermAccess[conference] = io.load(path, {})
	gTempAccess[conference] = {}

def freeLocalAccesses(conference):
	del gPermAccess[conference]
	del gTempAccess[conference]

def login(msgType, conference, nick, param):
	if msgType == protocol.TYPE_PRIVATE:
		if param == Config.ADMIN_PASSWORD:
			truejid = getTrueJID(conference, nick)
			if truejid not in Config.ADMINS:
				Config.ADMINS.append(truejid)
				setTempGlobalAccess(truejid, 100)
				sendMsg(msgType, conference, nick, u"Пароль принят, глобальный доступ выдан")
			else:
				sendMsg(msgType, conference, nick, u"Ошибка! Вы уже авторизованы!")
		else:
			sendMsg(msgType, conference, nick, u"Ошибка! Неверный пароль!")

def logout(msgType, conference, nick, param):
	truejid = getTrueJID(conference, nick)
	if truejid in Config.ADMINS:
		Config.ADMINS.remove(truejid)
		setTempGlobalAccess(truejid)
		sendMsg(msgType, conference, nick, u"Глобальный доступ снят")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка! Вы не авторизованы!")

def showUserAccess(msgType, conference, nick, param):
	user = param or nick
	truejid = getTrueJID(conference, user)
	if truejid:
		access = getAccess(conference, truejid)
		if access in ACCESS_DESC:
			accDesc = ACCESS_DESC[access]
			sendMsg(msgType, conference, nick, u"%d (%s)" % (access, accDesc))
		else:
			sendMsg(msgType, conference, nick, u"%d" % (access))
	else:
		sendMsg(msgType, conference, nick, u"А кто это?")

def setLocalAccess(msgType, conference, nick, param):
	args = param.split(None, 2)
	userNick = args[0].strip()
	truejid = getTrueJID(conference, userNick)
	if not truejid:
		print userNick
		print netutil.isJID(userNick)
		if netutil.isJID(userNick):
			truejid = userNick
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
	try:
		if len(args) > 1:
			newAccess = int(args[1])
			if newAccess > 100 or newAccess < -100:
				raise ValueError
		else:
			newAccess = 0

		userAccess = getAccess(conference, truejid)
		senderjid = getTrueJID(conference, nick)
		senderAccess = getAccess(conference, senderjid)

		if newAccess > senderAccess or senderAccess < userAccess:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
			return
		if newAccess != 0:
			if len(args) == 2:
				setTempAccess(conference, truejid, newAccess)
				sendMsg(msgType, conference, nick, u"Доступ выдан до выхода из конференции")
			else:
				setPermAccess(conference, truejid, newAccess)
				sendMsg(msgType, conference, nick, u"Выдан постоянный доступ")
		else:
			setPermAccess(conference, truejid, newAccess)
			sendMsg(msgType, conference, nick, u"Постоянный доступ снят")
	except ValueError:
		sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число от -100 до 100!")

def setGlobalAccess(msgType, conference, nick, param):
	args = param.split(None, 1)
	user = args[0].strip()
	truejid = None
	if isConferenceInList(conference):
		truejid = getTrueJID(conference, user)
	if not truejid:
		if netutil.isJID(user):
			truejid = user
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
	try:
		if len(args) > 1:
			newAccess = int(args[1])
			if newAccess > 100 or newAccess < -100:
				raise ValueError
		else:
			newAccess = 0
		setPermGlobalAccess(truejid, newAccess)
		if newAccess != 0:
			sendMsg(msgType, conference, nick, u"Выдан глобальный доступ")
		else:
			sendMsg(msgType, conference, nick, u"Глобальный доступ снят")
	except ValueError:
		sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число от -100 до 100!")

def showGlobalAccesses(msgType, conference, nick, param):
	if not gGlobalAccess:
		sendMsg(msgType, conference, nick, u"Нет глобальных уровней доступа!")
	else:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		elements = [u"%d) %s [%d]" % (i + 1, item, gGlobalAccess[item])
				for i, item in enumerate(sorted(gGlobalAccess))]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Глобальные уровни доступа:\n%s" % ("\n".join(elements)))

def showLocalAccesses(msgType, conference, nick, param):
	if not gPermAccess[conference]:
		sendMsg(msgType, conference, nick, u"Нет локальных уровней доступа!")
	else:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		accesses = gPermAccess[conference]
		elements = [u"%d) %s [%d]" % (i + 1, item, accesses[item])
				for i, item in enumerate(sorted(accesses))]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Локальные уровни доступа:\n%s" % ("\n".join(elements)))

registerEventHandler(loadGlobalAccesses, EVT_CONNECTED)

registerEventHandler(loadLocalAccesses, EVT_ADDCONFERENCE)
registerEventHandler(freeLocalAccesses, EVT_DELCONFERENCE)

registerCommand(login, u"логин", 0,
				u"Авторизоваться как админиcтратор бота",
				u"<пароль>",
				(u"secret", ),
				CMD_ANY | CMD_FROZEN | CMD_PARAM)
registerCommand(logout, u"логаут", 0,
				u"Разлогиниться",
				None,
				None,
				CMD_ANY | CMD_FROZEN | CMD_NONPARAM)
registerCommand(showUserAccess, u"доступ", 0,
				u"Показывает уровень доступа определённого пользователя",
				u"[ник|жид]",
				(None, u"Nick", u"user@server.tld"),
				CMD_CONFERENCE | CMD_FROZEN)
registerCommand(setLocalAccess, u"дать_доступ", 20,
				u"Устанавливает или снимает (если указать уровень доступа, равный 0, или вовсе не указывать его) уровень локального доступа для определённого пользователя на определённый уровень. Если указывается второй параметр (что угодно), то выдаётся постоянный доступ доступ",
				u"<ник|жид> <уровень> [навсегда]",
				(u"Nick 100", u"user@server.tld 100", u"Nick 100 1"),
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setGlobalAccess, u"глобдоступ", 100,
				u"Устанавливает или снимает (если указать уровень доступа, равный 0, или вовсе не указывать его) уровень глобального доступа для определённого пользователя",
				u"<ник|жид> [уровень]",
				(u"Nick", u"user@server.tld", u"Nick 100"),
				CMD_ANY | CMD_FROZEN | CMD_PARAM)
registerCommand(showGlobalAccesses, u"доступы", 100,
				u"Показывает все глобальные уровни доступа",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
registerCommand(showLocalAccesses, u"локалдоступы", 20,
				u"Показывает все локальные уровни доступа",
				None,
				None,
				CMD_CONFERENCE | CMD_NONPARAM)