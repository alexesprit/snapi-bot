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

SEND_FILE = "send.txt"

gSendCache = {}

def loadSendBase(conference):
	path = getConfigPath(conference, SEND_FILE)
	gSendCache[conference] = database.DataBase(path)

def freeSendBase(conference):
	del gSendCache[conference]

def addToSendBase(msgType, conference, nick, param):
	param = param.split(None, 1)
	if len(param) == 2:
		userNick = param[0]
		message = param[1]
		message = u"%s попросил меня передать тебе следующее:\n%s" % (nick, message)
		if isNickOnline(conference, userNick):
			sendMsg(protocol.TYPE_PRIVATE, conference, userNick, message)
			sendMsg(msgType, conference, nick, u"Передала")
		elif isNickInConference(conference, userNick):
			trueJid = getTrueJid(conference, userNick)
			base = gSendCache[conference]
			if trueJid not in base:
				base[trueJid] = []
			base[trueJid].append(message)
			base.save()
			sendMsg(msgType, conference, nick, u"Передам")
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")

def checkSendBase(conference, nick, trueJid, aff, role):
	base = gSendCache[conference]
	if trueJid in base:
		for message in base[trueJid]:
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
			time.sleep(0.5)
		del base[trueJid]
		base.save()

registerEvent(loadSendBase, EVT_ADDCONFERENCE)
registerEvent(freeSendBase, EVT_DELCONFERENCE)
registerJoinHandler(checkSendBase)

registerCommand(addToSendBase, u"передать", 10, 
				u"Запоминает сообщение и передаёт его указанному пользователю, как только он зайдёт в конференцию (или сразу, если указанный пользователь уже в конференции)", 
				u"<кому> <что>", 
				(u"Nick хай!", ), 
				CMD_CONFERENCE | CMD_PARAM)
