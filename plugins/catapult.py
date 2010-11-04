# coding: utf-8

# catapult.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def runCatapult(msgType, conference, nick, param):
	if not getNickKey(conference, nick, NICK_MODER):
		setMUCRole(conference, nick, protocol.ROLE_NONE, u"КАТАПУЛЬТИРУЮСЬ!")
	else:
		sendMsg(msgType, conference, nick, u"Модераторов не трогаю :)")

registerCommand(runCatapult, u"катапульту", 10, 
				u"Катапульта", 
				None, 
				(u"катапульту", ), 
				CHAT | NONPARAM)
