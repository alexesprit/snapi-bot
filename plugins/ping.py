# coding: utf-8

# ping.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) Gigabyte
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

PONG_REPLICS_FOR_OTHER = (
	u"Понг от %s составляет %s сек.", 
	u"Скорость отклика сервера для %s равна %s сек.", 
	u"Скорость отправки пакетов от %s составляет %s сек.", 
	u"Опа! Что я откопала! Это же понг от %s: %s сек."
)

PONG_REPLICS_FOR_ME = (
	u"Твой понг составляет %s сек.", 
	u"Скорость отклика сервера для тебя равна %s сек.", 
	u"Скорость отправки твоих пакетов равна %s сек.", 
	u"Опа! Что я откопала! Это же твой понг: %s сек."
)

def showPing(msgType, conference, nick, param):
	if param:
		usernick = param
		if isConferenceInList(conference) and \
			isNickOnline(conference, usernick):
				jid = u"%s/%s" % (conference, usernick)
		else:
			jid = param
	else:
		jid = u"%s/%s" % (conference, nick)
	iq = protocol.Iq(protocol.TYPE_GET)
	iq.addChild("ping", {}, [], protocol.NS_PING)
	iq.setTo(jid)
	t0 = time.time()
	gClient.sendAndCallForResponse(iq, showPing_, (t0, msgType, conference, nick, param))

def showPing_(stanza, t0, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		pong = str(round(time.time() - t0 , 3))
		if param:
			message = random.choice(PONG_REPLICS_FOR_OTHER) % (param, pong)
		else:
			message = random.choice(PONG_REPLICS_FOR_ME) % (pong)
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Не пингуется :(")

registerCommand(showPing, u"пинг", 10, 
				u"Пингует указанного пользователя или jabber-сервер", 
				u"[ник|жид|сервер]", 
				(None, u"Nick", u"server.tld", u"user@server.tld"))
