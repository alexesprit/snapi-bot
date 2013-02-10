# coding: utf-8

# here.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showHereTime(msgType, conference, nick, param):
	userNick = param or nick
	if isNickOnline(conference, userNick):
		rawtime = getNickKey(conference, userNick, NICK_JOINED)
		joinTime = getTimeStr(time.time() - rawtime)
		if not param:
			sendMsg(msgType, conference, nick, u"Ты уже здесь %s" % (joinTime))
		else:
			sendMsg(msgType, conference, nick, u"%s уже здесь %s" % (userNick, joinTime))
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

registerCommand(showHereTime, u"здесь", 10, 
				u"Показывает, сколько времени пользователь сидит в конференции", 
				u"[ник]", 
				(None, u"Nick"), 
				CMD_CONFERENCE)
