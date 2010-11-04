# coding: utf-8

# version.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showVersion(msgType, conference, nick, param):
	if param == getBotNick(conference):
		sendMsg(msgType, conference, nick, u"Я юзаю %s %s в %s" % (gVersion[0], gVersion[1], gVersion[2]))
	else:
		if param:
			if conferenceInList(conference) and nickIsOnline(conference, param):
				jid = conference + "/" + param
			else:
				jid = param
		else:
			jid = conference + "/" + nick
		iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_VERSION)
		iq.setTo(jid)
		iq.setID(getUniqueID("ver_id"))
		gClient.sendAndCallForResponse(iq, _showVersion, (msgType, conference, nick, param, ))

def _showVersion(stanza, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		name, ver, os = "", "", ""
		query = stanza.getQueryNode()
		name = query.getTagData("name")
		ver = query.getTagData("version")
		os = query.getTagData("os")
		version = u""
		if name:
			version += name
		if ver:
			version += u" " + ver
		if os:
			version += u" в " + os
		if version:
			if not param:
				sendMsg(msgType, conference, nick, u"Ты юзаешь %s" % (version))
			else:
				sendMsg(msgType, conference, nick, u"%s юзает %s" % (param, version))
		else:
			sendMsg(msgType, conference, nick, u"Клиент глюк, инфы не хватает")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showVersion, u"версия", 10, 
				u"Показывает информацию о версии ПО указанного пользователя или сервера", 
				u"версия [ник|сервер]", 
				(u"версия", u"версия Nick", u"версия server.tld"))
