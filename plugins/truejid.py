# coding: utf-8

# truejid.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showTrueJid(msgType, conference, nick, param):
	if isNickInConference(conference, param):
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Смотри в привате")
		trueJid = getTrueJid(conference, param)
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Жид %s: %s" % (param, trueJid))
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

registerCommand(showTrueJid, u"тружид", 20, 
				u"Показывает реальный жид указанного ника", 
				u"<ник>", 
				(u"Nick", ), 
				CMD_CONFERENCE | CMD_PARAM)
