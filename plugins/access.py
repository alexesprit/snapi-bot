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
	if(msgType == protocol.TYPE_PRIVATE and param == gAdminPass):
		trueJid = getTrueJid(conference, nick)
		setTempGlobalAccess(trueJid, 100)
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"пароль принят, полный доступ выдан")

def logout(msgType, conference, nick, parameters):
	trueJid = getTrueJid(conference, nick)
	setTempGlobalAccess(trueJid)
	sendMsg(msgType, conference, nick, u"глобальный доступ снят")

def showUserAccess(msgType, conference, nick, param):
	levelDesc = ""
	user = param
	if not param:
		userJid = getTrueJid(conference, nick)
	else:
		if conferenceInList(conference) and nickInConference(conference, user):
			userJid = getTrueJid(conference, user)
		elif isJid(user):
			userJid = user
		else:
			sendMsg(msgType, conference, nick, u"а кто это?")
			return
	access = getAccess(conference, userJid)
	if access in ACCESS_DESC:
		accDesc = ACCESS_DESC[access]
		sendMsg(msgType, conference, nick, u"%d (%s)" % (access, accDesc))
	else:
		sendMsg(msgType, conference, nick, u"%d" % (access))

def setLocalAccess(msgType, conference, nick, param):
	param = param.split()
	if len(param) < 4:
		user = param[0].strip()
		if nickInConference(conference, user):
			userJid = getTrueJid(conference, user)
		elif isJid(user):
			userJid = getTrueJid(conference, user)
		else:
			sendMsg(msgType, conference, nick, u"а кто это?")
			return
		try:
			access = int(param[1])
			if -100 <= access <= 100:
				userAccess = getAccess(conference, userJid)
				myJid = getTrueJid(conference, nick)
				myAccess = getAccess(conference, myJid)
				if access == userAccess:
					sendMsg(msgType, conference, nick, u"уровень доступа у %s уже %d!" % (user, access))
					return				
				if userAccess > myAccess or access > myAccess:
					sendMsg(msgType, conference, nick, u"недостаточно прав")
					return
				if len(param) == 2:
					setTempAccess(conference, userJid, access)
					sendMsg(msgType, conference, nick, u"доступ выдан до выхода из конференции")
				else:
					setPermAccess(conference, userJid, access)
					sendMsg(msgType, conference, nick, u"выдан постоянный доступ")
			else:
				sendMsg(msgType, conference, nick, u"уровнем доступа должно являться число от -100 до 100!")
		except ValueError:
			sendMsg(msgType, conference, nick, u"уровнем доступа должно являться число от -100 до 100!")
	else:
		sendMsg(msgType, conference, nick, u"ошибочный запрос")

def delLocalAccess(msgType, conference, nick, param):
	user = param
	if nickInConference(conference, user):
		userJid = getTrueJid(conference, user)
	elif isJid(user):
		userJid = getTrueJid(conference, user)
	else:
		sendMsg(msgType, conference, nick, u"а кто это?")
		return
	myJid = getTrueJid(conference, nick)
	myAccess = getAccess(conference, myJid)
	userAccess = getAccess(conference, userJid)
	if(userAccess > myAccess):
		sendMsg(msgType, conference, nick, u"недостаточно прав")
		return
	setPermAccess(conference, userJid)
	sendMsg(msgType, conference, nick, u"постоянный доступ снят")

def setGlobalAccess(msgType, conference, nick, param):
	param = param.split()
	if len(param) < 3:
		user = param[0].strip()
		if conferenceInList(conference):
			if nickInConference(conference, user):
				userJid = getTrueJid(conference, user)
			elif isJid(user):
				userJid = user
			else:
				sendMsg(msgType, conference, nick, u"а это кто?")
				return
		else:
			if isJid(user):
				userJid = user
			else:
				sendMsg(msgType, conference, nick, u"а это кто?")
				return
		if len(param) == 2:
			try:
				access = int(param[1])
				if -100 <= access <= 100:
					setPermGlobalAccess(userJid, int(access))
					sendMsg(msgType, conference, nick, u"дала")
				else:
					sendMsg(msgType, conference, nick, u"уровнем доступа должно являться число от -100 до 100!")
			except ValueError:
				sendMsg(msgType, conference, nick, u"уровнем доступа должно являться число от -100 до 100!")
		else:
			setPermGlobalAccess(userJid)
			sendMsg(msgType, conference, nick, u"сняла")
	else:
		sendMsg(msgType, conference, nick, u"ошибочный запрос")

def showGlobalAccesses(msgType, conference, nick, param):
	if(not gGlobalAccess):
		sendMsg(msgType, conference, nick, u"нет глобальных доступов")
	else:
		if(protocol.TYPE_PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u"ушли")
		items = [u"%s [%d]" % (jid, access) 
				for jid, access in gGlobalAccess.items()]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"вот, что я нашла\n" + "\n".join(items))

def showLocalAccesses(msgType, conference, nick, param):
	if(not gPermAccess[conference]):
		sendMsg(msgType, conference, nick, u"нет локальных доступов")
	else:
		if(protocol.TYPE_PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u"ушли")
		items = [u"%s [%d]" % (jid, access) 
				for jid, access in gPermAccess[conference].items()]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"вот, что я нашла\n" + "\n".join(items))

def loadGlobalAccesses():
	global gGlobalAccess
	fileName = getConfigPath(ACCESS_FILE)
	utils.createFile(fileName, "{}")
	gGlobalAccess = eval(utils.readFile(fileName))
	for jid in gAdmins:
		gGlobalAccess[jid] = 100

def loadLocalAccesses(conference):
	fileName = getConfigPath(conference, ACCESS_FILE)
	utils.createFile(fileName, "{}")
	gPermAccess[conference] = eval(utils.readFile(fileName))
	gTempAccess[conference] = {}

def freeLocalAccesses(conference):
	del(gPermAccess[conference])
	del(gTempAccess[conference])

registerEvent(loadGlobalAccesses, STARTUP)
registerEvent(loadLocalAccesses, ADDCONF)
registerEvent(freeLocalAccesses, DELCONF)

registerCommand(login, u"логин", 0,
				u"Авторизоваться как админиcтратор бота", 
				u"логин <пароль>",
				(u"логин secret", ), 
				ANY | FROZEN | PARAM)
registerCommand(logout, u"логаут", 0,
				u"Разлогиниться", 
				None, 
				(u"логаут", ), 
				ANY | FROZEN | NONPARAM)
registerCommand(showUserAccess, u"доступ", 0, 
				u"Показывает уровень доступа определённого пользователя", 
				u"доступ [ник]", 
				(u"доступ", u"доступ Nick"), 
				ANY | FROZEN)
registerCommand(setLocalAccess, u"дать_доступ", 20, 
				u"Устанавливает уровень локального доступа для определённого пользователя на определённый уровень. Если указывается второй параметр (что угодно), то выдаётся постоянный доступ доступ", 
				u"дать_доступ <ник|жид> <уровень> [навсегда]", 
				(u"дать_доступ Nick 100", u"дать_доступ Nick 100 1"), 
				CHAT | PARAM)
registerCommand(delLocalAccess, u"снять_доступ", 20, 
				u"Снимает уровень локального доступа для определённого пользователя.", 
				u"снять_доступ <ник|жид>", 
				(u"снять_доступ Nick", ), 
				CHAT | PARAM)
registerCommand(setGlobalAccess, u"глобдоступ", 100, 
				u"Устанавливает или снимает (если не писать уровень) уровень глобального доступа для определённого пользователя", 
				u"глобдоступ <ник|жид> [уровень]", 
				(u"глобдоступ guy", u"глобдоступ Nick 100"), 
				ANY | FROZEN | PARAM)
registerCommand(showGlobalAccesses, u"доступы", 100, 
				u"Показывает все глобальные уровни доступа", 
				None, 
				(u"доступы", ), 
				ANY | NONPARAM)
registerCommand(showLocalAccesses, u"локалдоступы", 20, 
				u"Показывает все локальные уровни доступа", 
				None, 
				(u"локалдоступы", ), 
				CHAT | NONPARAM)