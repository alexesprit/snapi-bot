# coding: utf-8

# roulette.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007-2008 Als <Als@exploit.in>>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def runCatapult(msgType, conference, nick, param):
	if not isNickModerator(conference, nick):
		setMUCRole(conference, nick, protocol.ROLE_NONE, u"КАТАПУЛЬТИРУЮСЬ!")
	else:
		sendMsg(msgType, conference, nick, u"Модераторов не трогаю :)")

def playRoulette(msgType, conference, nick, param):
	if not isNickModerator(conference, nick):
		if not random.randrange(0, 6):
			sendMsg(msgType, conference, nick, u"ЩЁЛК!")
		else:
			sendToConference(conference, u"/me выстрелила в %s" % (nick))
			time.sleep(1)
			setMUCRole(conference, nick, protocol.ROLE_NONE, u"ПЫЩЩЬ-ПТЫДЫЩЬ!")
	else:
		sendMsg(msgType, conference, nick, u"Модераторов не трогаю :)")

registerCommand(playRoulette, u"рр", 10, 
				u"Старая добрая русская рулетка", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(runCatapult, u"катапульту", 10, 
				u"Катапульта", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
