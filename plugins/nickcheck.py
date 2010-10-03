# coding: utf-8

# nickcheck.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def checkNick(stanza, conference, nick, trueJid):
	code = stanza.getStatusCode()
	nick = ("303" != code) and nick or stanza.getNick()
	if(nick.strip()):
		command = nick.split()[0].strip().lower()
		if(isCommand(command) or gMacros.hasMacros(command, conference) or gMacros.hasMacros(command)):
			setRole(conference, nick, xmpp.ROLE_NONE, u"меняй ник!!!")

registerPresenceHandler(checkNick, CHAT)
