# coding: utf-8

# manage.py
# Initial Copyright (c) ???
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def joinConf(msgType, conference, nick, param):
	args = param.split()
	if param and netutil.isJID(args[0]):
		joinRoom = args[0]
		if isConferenceInList(joinRoom):
			sendMsg(msgType, conference, nick, u"Я уже там!")
		else:
			addConference(joinRoom)
			password = (len(args) == 2) and args[1] or None
			setConferenceConfigKey(joinRoom, "nick", getBotNick(joinRoom))
			setConferenceConfigKey(joinRoom, "password", password)
			joinConference(joinRoom)
			saveConferenceConfig(joinRoom)
			saveConferences()
			sendMsg(msgType, conference, nick, u"Зашла")

def leaveConf(msgType, conference, nick, param):
	joinRoom = param or conference
	if isConferenceInList(joinRoom):
		if joinRoom != conference:
			sendMsg(msgType, conference, nick, u"Ушла")
		myNick = getNickFromJID(conference, nick)
		leaveConference(joinRoom, u"Меня уводит %s" % (myNick))
		saveConferences()
	else:
		if param:
			sendMsg(msgType, conference, nick, u"А меня там и нет!")
		else:
			sendMsg(msgType, conference, nick, u"Ошибка! Необходимо указать конференцию")
			
def updateWorkingCopy(msgType, conference, nick, param):
	response = os.popen("svn up").read()
	if response:
		currentRev = Version.revision
		newRev = os.popen("svnversion -n").read()
		if currentRev != newRev:
			sendMsg(msgType, conference, nick, u"Обновлено до редакции %s" % (newRev))
			stop(ACTION_RESTART, u"Выключаюсь: обновление")
		else:
			sendMsg(msgType, conference, nick, u"Ваша копия не требует обновления")
	else:
		sendMsg(msgType, conference, nick, u"Не удалось обновиться, возможно не установлена SubVersion")

def botRestart(msgType, conference, nick, param):
	myNick = getNickFromJID(conference, nick)
	if param:
		message = u"Меня перезагружает %s: %s" % (myNick, param)
	else:
		message = u"Меня перезагружает %s" % (myNick)
	stop(ACTION_RESTART, message)

def botShutdown(msgType, conference, nick, param):
	myNick = getNickFromJID(conference, nick)
	if param:
		message = u"Меня выключает %s: %s" % (myNick, param)
	else:
		message = u"Меня выключает %s" % (myNick)
	stop(ACTION_SHUTDOWN, message)

registerCommand(joinConf, u"зайти", 100,
				u"Заставляет бота войти в указанную конференцию",
				u"<конференция> [пароль]",
				(u"room@conference.server.tld", u"room@conference.server.tld secret"),
				CMD_ANY | CMD_PARAM)
registerCommand(leaveConf, u"свали",
				30, u"Заставляет бота выйти из указанной конференции",
				u"[конференция]",
				(None, u"room@conference.server.tld"))
registerCommand(updateWorkingCopy, u"update", 100,
				u"Обновление рабочей копии бота",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
registerCommand(botRestart, u"рестарт", 100, 
				u"Перезапускает бота", 
				u"[причина]", 
				(None, u"обновление"), 
				CMD_ANY | CMD_FROZEN)
registerCommand(botShutdown, u"идиспать", 100, 
				u"Выключает бота", 
				u"[причина]", 
				(None, u"тех. работы"), 
				CMD_ANY | CMD_FROZEN)
