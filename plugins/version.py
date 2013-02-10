# coding: utf-8

# version.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showVersion(msgType, conference, nick, param):
	if param:
		usernick = param
		if isConferenceInList(conference) and \
			isNickOnline(conference, usernick):
				jid = u"%s/%s" % (conference, usernick)
		else:
			jid = param
	else:
		jid = u"%s/%s" % (conference, nick)
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_VERSION, to=jid)
	gClient.sendAndCallForResponse(iq, showVersion_, (msgType, conference, nick, param))

def showVersion_(stanza, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		query = stanza.getQueryNode()
		name = query.getTagData("name")
		ver = query.getTagData("version")
		os = query.getTagData("os")

		buf = []
		if name:
			buf.append(name)
		if ver:
			buf.append(ver)
		if os:
			buf.append(u"/ %s" % (os))
		if buf:
			if not param:
				sendMsg(msgType, conference, nick, u"Ты юзаешь %s" % (" ".join(buf)))
			else:
				sendMsg(msgType, conference, nick, u"%s юзает %s" % (param, " ".join(buf)))
		else:
			sendMsg(msgType, conference, nick, u"Клиент глюк, инфы не хватает")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showVersion, u"версия", 10, 
				u"Показывает информацию о версии ПО указанного пользователя или jabber-сервера", 
				u"[ник|жид|сервер]", 
				(None, u"Nick", u"server.tld", u"user@server.tld"))
