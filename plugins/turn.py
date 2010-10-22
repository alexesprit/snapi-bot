# coding: utf-8

# turn.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TURN_TIMEOUT = 0.6

BIG_RU = u"ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,?Ё"
BIG_EN = u"QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?&~"
SML_RU = u"йцукенгшщзхъфывапролджэячсмитьбю.ё"
SML_EN = u"qwertyuiop[]asdfghjkl;'zxcvbnm,./`"

TABLE_BIG = dict(zip(BIG_RU + BIG_EN, BIG_EN + BIG_RU))
TABLE_SML = dict(zip(SML_RU + SML_EN, SML_EN + SML_RU))

gTurnMsgCache = {}

def getBigChar(char):
	return(TABLE_BIG.get(char, char))

def getSmlChar(char):
	return(TABLE_SML.get(char, char))

def turnMessage(text):
	text = "".join(map(getSmlChar, text))
	text = "".join(map(getBigChar, text))
	return(text)

def turnLastMessage(msgType, conference, nick, param):
	if(not msgType == protocol.TYPE_PUBLIC):
		sendMsg(msgType, conference, nick, u"тока в чате")
		return
	if(param):
		sendMsg(msgType, conference, nick, turnMessage(param))
	else:
		trueJid = getTrueJid(conference, nick)
		if(trueJid not in gTurnMsgCache[conference]):
			sendMsg(msgType, conference, nick, u"а ты ещё ничего не говорил")
		elif(gTurnMsgCache[conference][trueJid].lower() == u"turn"):
			sendMsg(msgType, conference, nick, u"последнее, что ты сказал, это \"turn\" :-D")
		else:
			savedMsg = gTurnMsgCache[conference][trueJid]
			receiver = None
			for userNick in getNicks(conference):
				if(savedMsg.startswith(userNick)):
					for x in [userNick + x for x in (":", ",")]:
						if(savedMsg.startswith(x)):
							savedMsg = savedMsg.replace(x, turnMessage(x))
							receiver = userNick
				if(receiver):
					break
			if(receiver):
				sendToConference(conference, u"%s (от %s)" % (turnMessage(savedMsg), nick))
			else:
				sendMsg(msgType, conference, nick, turnMessage(savedMsg))

def saveTurnMessage(stanza, msgType, conference, nick, trueJid, body):
	if(msgType == protocol.TYPE_PUBLIC):
		if(trueJid != gJid and trueJid != conference):
			time.sleep(TURN_TIMEOUT)
			gTurnMsgCache[conference][trueJid] = body

def initTurnCache(conference):
	gTurnMsgCache[conference] = {}

def freeTurnCache(conference):
	del(gTurnMsgCache[conference])

def clearTurnCache(conference, nick, trueJid, reason, code):
	if(trueJid in gTurnMsgCache[conference]):
		del(gTurnMsgCache[conference][trueJid])

registerEvent(initTurnCache, ADDCONF)
registerEvent(freeTurnCache, DELCONF)
registerLeaveHandler(clearTurnCache)
registerMessageHandler(saveTurnMessage, CHAT)

registerCommand(turnLastMessage, u"turn", 10, 
				u"Переключает раскладку вашего последнего сообщения или текста в параметре команды", 
				u"turn [текст]", 
				(u"turn", u"turn jkjkj"), 
				CHAT)
