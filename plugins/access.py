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
	0: u"(никто)", 
	10: u"(юзер)", 
	11: u"(мембер)", 
	15: u"(модер)", 
	16: u"(модер)", 
	20: u"(админ)", 
	30: u"(овнер)", 
	100: u"(админ бота)",
	-100: u"(игнор)"
}

def login(msgType, conference, nick, param):
	if(msgType == protocol.TYPE_PRIVATE and param == gAdminPass):
		trueJid = getTrueJid(conference, nick)
		setTempGlobalAccess(trueJid, 100)
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"пароль принят, полный доступ выдан")

def logout(msgType, conference, nick, parameters):
	trueJid = getTrueJid(conference, nick)
	setTempGlobalAccess(trueJid)
	sendMsg(msgType, conference, nick, u"доступ снят")

def showUserAccess(msgType, conference, nick, param):
	levelDesc = ""
	if(not param):
		trueJid = getTrueJid(conference, nick)
		level = getAccess(conference, trueJid);	
	else:
		if(conferenceInList(conference) and nickInConference(conference, param)):
			trueJid = getTrueJid(conference, param)
		else:
			sendMsg(msgType, conference, nick, u"а кто это?")
			return
	level = getAccess(conference, trueJid)
	if(level in ACCESS_DESC):
		levelDesc = ACCESS_DESC[level]
	sendMsg(msgType, conference, nick, u"%d %s" % (level, levelDesc))

def setLocalAccess(msgType, conference, nick, param):
	param = param.split()
	userNick = param[0].strip()
	if(nickInConference(conference, userNick)):
		access = 0
		if(len(param) > 1):
			try:
				access = int(param[1])
				if(100 < access or access < -100):
					sendMsg(msgType, conference, nick, u"ошибочный запрос")
					return
			except(ValueError):
				sendMsg(msgType, conference, nick, u"ошибочный запрос")
				return
		myJid = getTrueJid(conference, nick)
		myAccess = getAccess(conference, myJid)
		userJid = getTrueJid(conference, userNick)
		userAccess = getAccess(conference, userJid)
		if(userAccess > myAccess or access > myAccess):
			sendMsg(msgType, conference, nick, u"недостаточно прав")
			return
		if(len(param) == 1):
			setPermAccess(conference, userJid)
			sendMsg(msgType, conference, nick, u"постоянный доступ снят")
		elif(len(param) == 2):
			setTempAccess(conference, userJid, access)
			sendMsg(msgType, conference, nick, u"доступ выдан до выхода из конференции")
		elif(len(param) == 3):
			setPermAccess(conference, userJid, access)
			sendMsg(msgType, conference, nick, u"выдан постоянный доступ")
	else:
		sendMsg(msgType, conference, nick, u"а кто это?")

def setGlobalAccess(msgType, conference, nick, param):
	param = param.split()
	if(len(param) < 1 or len(param) > 2):
		sendMsg(msgType, conference, nick, u"ошибочный запрос")
		return
	userNick = param[0].strip()
	if(conferenceInList(conference)):
		if(nickInConference(conference, userNick)):
			trueJid = getTrueJid(conference, userNick)
		else:
			sendMsg(msgType, conference, nick, u"а это кто?")
			return
	else:
		if(userNick.count("@")):
			trueJid = userNick
		else:
			sendMsg(msgType, conference, nick, u"а это кто?")
			return
	if(len(param) == 2):
		try:
			access = int(param[1])
			if(-100 <= access <= 100):
				setPermGlobalAccess(trueJid, int(access))
				sendMsg(msgType, conference, nick, u"дала")
			else:
				sendMsg(msgType, conference, nick, u"ошибочный запрос")
		except(ValueError):
			sendMsg(msgType, conference, nick, u"ошибочный запрос")
	else:
		setPermGlobalAccess(trueJid)
		sendMsg(msgType, conference, nick, u"сняла")

def showGlobalAccesses(msgType, conference, nick, param):
	if(not gGlobalAccess):
		sendMsg(msgType, conference, nick, u"нет глобальных доступов")
	else:
		if(protocol.TYPE_PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u"ушли")
		items = [u"%s [%d]" % (jid, gGlobalAccess[jid]) for jid in gGlobalAccess]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"вот, что я нашла\n" + "\n".join(items))

def showLocalAccesses(msgType, conference, nick, param):
	if(not gPermAccess[conference]):
		sendMsg(msgType, conference, nick, u"нет локальных доступов")
	else:
		if(protocol.TYPE_PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u"ушли")
		items = [u"\n%s [%d]" % (jid, gPermAccess[conference][jid]) for jid in gPermAccess[conference]]
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
				u"Устанавливает или снимает (если не писать уровень) уровень доступа для определённого пользователя на определённый уровень. Если указываеться третий параметр, то изменение происходит навсегда", 
				u"дать_доступ <ник> [уровень] [навсегда]", 
				(u"дать_доступ Nick 100", u"дать_доступ Nick 100 1"), 
				CHAT | PARAM)
registerCommand(setGlobalAccess, u"глобдоступ", 100, 
				u"Устанавливает или снимает (если не писать уровень) уровень доступа для определённого пользователя на определённый уровень глобально", 
				u"глобдоступ <ник|жид> [уровень]", 
				(u"глобдоступ guy", u"глобдоступ Nick 100"), 
				ANY | FROZEN | PARAM)
registerCommand(showGlobalAccesses, u"доступы", 100, 
				u"Показывает все глобальные доступы", 
				None, 
				(u"доступы", ), 
				ANY | NONPARAM)
registerCommand(showLocalAccesses, u"локалдоступы", 20, 
				u"Показывает все локальные доступы", 
				None, 
				(u"локалдоступы", ), 
				CHAT | NONPARAM)