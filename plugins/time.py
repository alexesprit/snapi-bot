# coding: utf-8

# time.py
# Initial Copyright (с) 2007 Als <Als@exploit.in>
# Modification Copyright (с) 2007 dimichxp <dimichxp@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showUserTime(msgType, conference, nick, param):
	if param:
		if isConferenceInList(conference) and isNickOnline(conference, param):
			jid = conference + "/" + param
		else:
			jid = param
	else:
		jid = conference + "/" + nick
	iq = protocol.Iq(protocol.TYPE_GET)
	iq.addChild("time", {}, [], protocol.NS_ENTITY_TIME)
	iq.setTo(jid)
	iq.setID(getUniqueID("time_id"))
	gClient.sendAndCallForResponse(iq, _showUserTime, (msgType, conference, nick, param))

def _showUserTime(stanza, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		timeNode = stanza.getTag("time")
		tzo = timeNode.getTagData("tzo")
		utc = timeNode.getTagData("utc")
		if tzo and utc:
			sign, tzHour, tzMin = re.match("(\+|-)?([0-9]+):([0-9]+)", tzo).groups()
			offset = int(tzHour) * 3600 + int(tzMin) * 60
			if sign == "-":
				offset = -offset
			rawTime = time.strptime(utc, "%Y-%m-%dT%H:%M:%SZ")
			rawTime = time.mktime(rawTime) + offset
			userTime = time.strftime("%H:%M:%S (%d.%m.%y)", time.localtime(rawTime))
			if param:
				sendMsg(msgType, conference, nick, u"У %s сейчас %s" % (param, userTime))
			else:
				sendMsg(msgType, conference, nick, u"У тебя сейчас %s" % (userTime))
		else:
			sendMsg(msgType, conference, nick, u"Клиент глюк, инфы не хватает")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showUserTime, u"часики", 10, 
				u"Показывает время указанного пользователя или сервера", 
				u"[ник|сервер]", 
				(None, u"Nick", u"server.tld", u"user@server.tld"))
