# coding: utf-8

# ping.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) Gigabyte

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

REPLICS_FOR_OTHER = (
	u"Понг от %s составляет", 
	u"Скорость отклика сервера для %s равна", 
	u"Скорость отправки пакетов от %s составляет", 
	u"Опа! Что я откопала! Это же понг от %s:"
)

REPLICS_FOR_ME = (
	u"Твой понг составляет", 
	u"Скорость отклика сервера для тебя равна", 
	u"Скорость отправки твоих пакетов равна", 
	u"Опа! Что я откопала! Это же твой понг:"
)

def _showPing(stanza, t0, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		ping = time.time() - t0
		if param:
			message = random.choice(REPLICS_FOR_OTHER) % (param);  
		else:
			message = random.choice(REPLICS_FOR_ME)
		message += u" %s сек." % (str(round(ping , 3)))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"не пингуется :(")

def showPing(msgType, conference, nick, param):
	if param:
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			jid = conference + "/" + param
		else:
			jid = param
	else:
		jid = conference + "/" + nick
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_VERSION)
	iq.setTo(jid)
	iq.setID(getUniqueID("ping_id"))
	t0 = time.time()
	gClient.sendAndCallForResponse(iq, _showPing, (t0, msgType, conference, nick, param, ))

registerCommand(showPing, u"пинг", 10, 
				u"Пингует тебя, определённый ник или сервер", 
				u"пинг [ник|сервер]", 
				(u"пинг", u"пинг Nick", u"пинг server.tld"))
