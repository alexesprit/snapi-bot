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

def showTrueJID(msgType, conference, nick, param):
	truejid = getTrueJID(conference, param)
	if truejid:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Смотри в привате")		
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Жид %s: %s" % (param, truejid))
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

registerCommand(showTrueJID, u"тружид", 20, 
				u"Показывает реальный жид указанного ника", 
				u"<ник>", 
				(u"Nick", ), 
				CMD_CONFERENCE | CMD_PARAM)
