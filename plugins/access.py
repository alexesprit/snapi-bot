# coding: utf-8

# access.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) Als <Als@exploit.in>
# Modification Copyright (c) 2010 -Esprit-

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

def login(msgType, conference, nick, param):
	if msgType == protocol.TYPE_PRIVATE:
		if param == gConfig.ADMIN_PASSWORD:
			trueJid = getTrueJid(conference, nick)
			if trueJid not in gConfig.ADMINS:
				gConfig.ADMINS.append(trueJid)
				setTempGlobalAccess(trueJid, 100)
				sendMsg(msgType, conference, nick, u"Пароль принят, глобальный доступ выдан")
			else:
				sendMsg(msgType, conference, nick, u"Ошибка! Вы уже авторизованы!")
		else:
			sendMsg(msgType, conference, nick, u"Ошибка! Неверный пароль!")

def logout(msgType, conference, nick, parameters):
	trueJid = getTrueJid(conference, nick)
	if trueJid in gConfig.ADMINS:
		gConfig.ADMINS.remove(trueJid)
		setTempGlobalAccess(trueJid)
		sendMsg(msgType, conference, nick, u"Глобальный доступ снят")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка! Вы не авторизованы!")

def showUserAccess(msgType, conference, nick, param):
	levelDesc = ""
	user = param
	if not param:
		userJid = getTrueJid(conference, nick)
	else:
		if isConferenceInList(conference) and isNickInConference(conference, user):
			userJid = getTrueJid(conference, user)
		elif isJid(user):
			userJid = user
		else:
			sendMsg(msgType, conference, nick, u"А кто это?")
			return
	access = getAccess(conference, userJid)
	if access in ACCESS_DESC:
		accDesc = ACCESS_DESC[access]
		sendMsg(msgType, conference, nick, u"%d (%s)" % (access, accDesc))
	else:
		sendMsg(msgType, conference, nick, u"%d" % (access))

def setLocalAccess(msgType, conference, nick, param):
	param = param.split(None, 2)
	user = param[0].strip()
	if isNickInConference(conference, user):
		userJid = getTrueJid(conference, user)
	elif isJid(user):
		userJid = getTrueJid(conference, user)
	else:
		sendMsg(msgType, conference, nick, u"А кто это?")
		return
	try:
		access = int(param[1])
		if -100 <= access <= 100:
			userAccess = getAccess(conference, userJid)
			myJid = getTrueJid(conference, nick)
			myAccess = getAccess(conference, myJid)
			if access == userAccess:
				sendMsg(msgType, conference, nick, u"Уровень доступа у %s уже %d!" % (user, access))
				return				
			if userAccess > myAccess or access > myAccess:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
				return
			if len(param) == 2:
				setTempAccess(conference, userJid, access)
				sendMsg(msgType, conference, nick, u"Доступ выдан до выхода из конференции")
			else:
				setPermAccess(conference, userJid, access)
				sendMsg(msgType, conference, nick, u"Выдан постоянный доступ")
		else:
			raise ValueError
	except ValueError:
		sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число от -100 до 100!")

def delLocalAccess(msgType, conference, nick, param):
	user = param
	if isNickInConference(conference, user):
		userJid = getTrueJid(conference, user)
	elif isJid(user):
		userJid = getTrueJid(conference, user)
	else:
		sendMsg(msgType, conference, nick, u"А кто это?")
		return
	myJid = getTrueJid(conference, nick)
	myAccess = getAccess(conference, myJid)
	userAccess = getAccess(conference, userJid)
	if userAccess > myAccess:
		sendMsg(msgType, conference, nick, u"Недостаточно прав")
		return
	setPermAccess(conference, userJid)
	sendMsg(msgType, conference, nick, u"Постоянный доступ снят")

def setGlobalAccess(msgType, conference, nick, param):
	param = param.split(None, 1)
	user = param[0].strip()
	if isConferenceInList(conference):
		if isNickInConference(conference, user):
			userJid = getTrueJid(conference, user)
		elif isJid(user):
			userJid = user
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
	else:
		if isJid(user):
			userJid = user
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
	if len(param) == 2:
		try:
			access = int(param[1])
			if -100 <= access <= 100:
				setPermGlobalAccess(userJid, access)
				sendMsg(msgType, conference, nick, u"Выдан глобальный доступ")
			else:
				raise ValueError
		except ValueError:
			sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число от -100 до 100!")
	else:
		setPermGlobalAccess(userJid)
		sendMsg(msgType, conference, nick, u"Сняла")

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

def loadGlobalAccesses():
	global gGlobalAccess
	path = getConfigPath(ACCESS_FILE)
	utils.createFile(path, "{}")
	gGlobalAccess = eval(utils.readFile(path))
	for jid in gConfig.ADMINS:
		gGlobalAccess[jid] = 100

def loadLocalAccesses(conference):
	path = getConfigPath(conference, ACCESS_FILE)
	utils.createFile(path, "{}")
	gPermAccess[conference] = eval(utils.readFile(path))
	gTempAccess[conference] = {}

def freeLocalAccesses(conference):
	del gPermAccess[conference]
	del gTempAccess[conference]

registerEventHandler(loadGlobalAccesses, EVT_STARTUP)
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
				u"Устанавливает уровень локального доступа для определённого пользователя на определённый уровень. Если указывается второй параметр (что угодно), то выдаётся постоянный доступ доступ", 
				u"<ник|жид> <уровень> [навсегда]", 
				(u"Nick 100", u"user@server.tld 100", u"Nick 100 1"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delLocalAccess, u"снять_доступ", 20, 
				u"Снимает уровень локального доступа для определённого пользователя.", 
				u"<ник|жид>", 
				(u"Nick", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(setGlobalAccess, u"глобдоступ", 100, 
				u"Устанавливает или снимает (если не писать уровень) уровень глобального доступа для определённого пользователя", 
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