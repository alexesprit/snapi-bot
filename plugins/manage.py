# coding: utf-8

# manage.py
# Initial Copyright (c) ???

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

registerCommand(joinConf, u"зайти", 100,
				u"Заставляет бота войти в указанную конференцию",
				u"<конференция> [пароль]",
				(u"room@conference.server.tld", u"room@conference.server.tld secret"),
				CMD_ANY | CMD_PARAM)
registerCommand(leaveConf, u"свали",
				30, u"Заставляет бота выйти из указанной конференции",
				u"[конференция]",
				(None, u"room@conference.server.tld"))
