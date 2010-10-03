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

gSend = {}

def loadSendCache(conference):
	fileName = getConfigPath(conference, SEND_FILE)
	gSend[conference] = database.DataBase(fileName)

def unloadSendCache(conference):
	del(gSend[conference])

def addMessageToQueue(msgType, conference, nick, param):
	param = param.split(None, 1)
	if(len(param) == 2):
		userNick = param[0]
		message = param[1]
		message = u"%s попросил меня передать тебе следующее:\n%s" % (nick, message)
		if(nickIsOnline(conference, userNick)):
			sendMsg(xmpp.TYPE_PRIVATE, conference, userNick, message)
			sendMsg(msgType, conference, nick, u"передала")
		elif(nickInConference(conference, userNick)):
			trueJid = getTrueJid(conference, userNick)
			base = gSend[conference]
			if(trueJid not in base):
				base[trueJid] = []
			base[trueJid].append(message)
			base.save()
			sendMsg(msgType, conference, nick, u"передам")
		else:
			sendMsg(msgType, conference, nick, u"а это кто?")

def checkQueue(conference, nick, trueJid, aff, role):
	base = gSend[conference]
	if(trueJid in base):
		for message in base[trueJid]:
			sendMsg(xmpp.TYPE_PRIVATE, conference, nick, message)
			time.sleep(0.5)
		del(base[trueJid])
		base.save()

registerEvent(loadSendCache, ADDCONF)
registerEvent(unloadSendCache, DELCONF)
registerJoinHandler(checkQueue)

registerCommand(addMessageToQueue, u"передать", 10, 
				u"Запоминает сообщение и передаёт его указанному пользователю, как только он зайдёт в конференцию", 
				u"передать <кому> <что>", 
				(u"передать Nick хай!", ), 
				CHAT)
