# coding: utf-8

# send.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Help Copyright (c) 2007 dimichxp <dimichxp@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

SEND_FILE = "send.dat"

gSendCache = {}

def loadSendBase(conference):
	path = getConfigPath(conference, SEND_FILE)
	gSendCache[conference] = database.DataBase(path)

def freeSendBase(conference):
	del gSendCache[conference]

def addToSendBase(msgType, conference, nick, param):
	args = param.split(None, 1)
	if len(args) == 2:
		userNick = args[0]
		message = args[1]
		message = u"%s попросил меня передать тебе следующее:\n%s" % (nick, message)
		if isNickOnline(conference, userNick):
			sendMsg(protocol.TYPE_PRIVATE, conference, userNick, message)
			sendMsg(msgType, conference, nick, u"Передала")
		elif isNickInConference(conference, userNick):
			truejid = getTrueJID(conference, userNick)
			base = gSendCache[conference]
			if truejid not in base:
				base[truejid] = []
			base[truejid].append(message)
			base.save()
			sendMsg(msgType, conference, nick, u"Передам")
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")

def sendMessagesToUser(conference, nick, truejid, aff, role):
	base = gSendCache[conference]
	if truejid in base:
		for message in base[truejid]:
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
			time.sleep(0.5)
		del base[truejid]
		base.save()

registerEventHandler(loadSendBase, EVT_ADDCONFERENCE)
registerEventHandler(freeSendBase, EVT_DELCONFERENCE)

registerEventHandler(sendMessagesToUser, EVT_USERJOIN)

registerCommand(addToSendBase, u"передать", 10, 
				u"Запоминает и передаёт сообщение указанному пользователю, как только он зайдёт в конференцию (или сразу, если указанный пользователь уже в конференции)",
				u"<кому> <что>", 
				(u"Nick хай!", ), 
				CMD_CONFERENCE | CMD_PARAM)
