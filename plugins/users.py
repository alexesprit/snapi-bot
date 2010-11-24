# coding: utf-8

# users.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showInMucUsers(msgType, conference, nick, param):
	items = [u"%d) %s" % (i + 1, user) 
			for i, user in enumerate(sorted(getOnlineNicks(conference)))]
	message = u"Я вижу здесь %d участников:\n%s" % (len(items), "\n".join(items))
	sendMsg(msgType, conference, nick, message)

def showWhoWas(msgType, conference, nick, param):
	items = [u"%d) %s" % (i + 1, user) 
			for i, user in enumerate(sorted(getNicks(conference)))]
	message = u"Я видела здесь %d участников:\n%s" % (len(items), "\n".join(items))
	sendMsg(msgType, conference, nick, message)
	
def showUserNicks(msgType, conference, nick, param):
	userNick = param or nick
	if isNickInConference(conference, userNick):
		trueJid = getTrueJid(conference, userNick)
		nicks = [user for user in getNicks(conference) 
				if trueJid == getTrueJid(conference, user)]
		if len(nicks) < 2:
			if param:
				sendMsg(msgType, conference, nick, u"Я знаю тебя только как %s" % (userNick))
			else:
				sendMsg(msgType, conference, nick, u"Я знаю %s только как %s")
		else:
			nicks.sort()
			if param:
				sendMsg(msgType, conference, nick, u"Я знаю %s как %s" % (userNick, ", ".join(nicks)))
			else:
				sendMsg(msgType, conference, nick, u"Я знаю тебя как %s" % (", ".join(nicks)))
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

registerCommand(showInMucUsers, u"инмук", 10, 
				u"Показывает список участников, находящихся в конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showWhoWas, u"хтобыл", 10, 
				u"Показывает список участников, посетивших конференцию за сессию", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showUserNicks, u"ники", 10, 
				u"Выводит все ники пользователя", 
				u"[ник]", 
				(None, u"Nick"),
				CMD_CONFERENCE)
