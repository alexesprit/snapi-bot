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
	param = param.split()
	if param and isJid(param[0]):
		conf = param[0]
		if isConferenceInList(conf):
			sendMsg(msgType, conference, nick, u"Я уже там!")
		else:
			password = (len(param) == 2) and param[1] or None
			EVT_ADDCONFerence(conf)
			joinConference(conf, gBotNick, getConferenceConfigKey(conf, "password"))
			saveConferenceConfig(conf)
			saveConferences()
			sendMsg(msgType, conference, nick, u"Зашла")

def leaveConf(msgType, conference, nick, param):
	conf = param or conference
	if isConferenceInList(conf):
		if conf != conference:
			sendMsg(msgType, conference, nick, u"Ушла")
		myNick = (isConferenceInList(conference)) and nick or conference.split("@")[0]
		leaveConference(conf, u"Меня уводит %s" % (myNick))
		saveConferences()
	else:
		if param:
			sendMsg(msgType, conference, nick, u"А меня там и нет!")
		else:
			sendMsg(msgType, conference, nick, u"Ошибка! Необходимо указать конференцию")

registerCommand(joinConf, u"зайти", 100, 
				u"Зайти в указанную конференцию", 
				u"<конференция> [пароль]", 
				(u"room@conference.server.tld", u"room@conference.server.tld"),
				CMD_ANY | CMD_PARAM)
registerCommand(leaveConf, u"свали", 
				30, u"Заставляет выйти из текущей или указанной конференции", 
				u"[конференция]", 
				(None, u"room@conference.server.tld"))
