# coding: utf-8

# chatterbox.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

MAX_MSG_COUNT = 100
MSG_COUNT_TO_SAVE = 20
SAVE_CHANCE = 25; # chance 1 of SAVE_CHANCE
REPLY_CHANCE = 35; # it"s the same.

CHATTERBOX_FILE = "chatterbox.txt"

gChatterCache = {}
gUpdateCount = {}

def removeNicks(message, nickList):
	nickFound = False
	_startswith = message.startswith
	for nick in nickList:
		if(_startswith(nick)):
			for x in [nick + x for x in (":", ",")]:
				if(_startswith(x)):
					message = message.replace(x, "")
					nickFound = True
		if(nickFound):
			break
	return(message)

def processChatter(stanza, msgType, conference, nick, trueJid, message):
	if(xmpp.TYPE_PUBLIC == msgType and getConfigKey(conference, "chatterbox")):
		if(not nick): # topic
			return
		botNick = getBotNick(conference)
		if(nick == botNick):
			return

		isHiglight = message.startswith(botNick)

		if(isHiglight or not random.randrange(0, REPLY_CHANCE)):
			message = removeNicks(message, getNicks(conference)).strip()
			if(message):
				command = message.split()[0].lower()
				_isCommand = isCommand(command) and isCommandType(command, CHAT)
				_isMacros = gMacros.hasMacros(command, conference) or gMacros.hasMacros(command)
				if(_isCommand or _isMacros):
					return
				if(gChatterCache[conference]):
					text = random.choice(gChatterCache[conference])
					isMe = text.startswith("/me")
					time.sleep(len(text) / 4 + random.randrange(1, 5))
					if(not isMe and (isHiglight or not random.randrange(0, 2))):
						sendMsg(msgType, conference, nick, text, True)
					else:
						sendToConference(conference, text)
		if(isHiglight or not random.randrange(0, SAVE_CHANCE)):
			message = removeNicks(message, getNicks(conference)).strip()
			if(message):
				command = message.split()[0]
				if(isCommand(command) or gMacros.hasMacros(command, conference) or gMacros.hasMacros(command)):
					return
				if(len(gChatterCache[conference]) >= MAX_MSG_COUNT):
					randNum = random.randrange(0, MAX_MSG_COUNT)
					del(gChatterCache[conference][randNum])
				gChatterCache[conference].append(message)
				gUpdateCount[conference] += 1
				if(gUpdateCount[conference] >= MSG_COUNT_TO_SAVE):
					fileName = getConfigPath(conference, CHATTERBOX_FILE)
					writeFile(fileName, str(gChatterCache[conference]))
					gUpdateCount[conference] = 0

def loadChatterBase(conference):
	fileName = getConfigPath(conference, CHATTERBOX_FILE)
	createFile(fileName, "[]")
	gChatterCache[conference] = eval(readFile(fileName))
	gUpdateCount[conference] = 0

	if(getConfigKey(conference, "chatterbox") is None):
		setConfigKey(conference, "chatterbox", 0)

def freeChatterBase(conference):
	del(gChatterCache[conference])

def chatterControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param == 1):
				setConfigKey(conference, "chatterbox", 1)
				sendMsg(msgType, conference, nick, u"болталка включена")
			else:
				setConfigKey(conference, "chatterbox", 0)
				sendMsg(msgType, conference, nick, u"болталка отключена")
			saveChatConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"текущее значение: %d" % (getConfigKey(conference, "chatterbox")))

registerEvent(loadChatterBase, ADDCONF)
registerEvent(freeChatterBase, DELCONF)
registerMessageHandler(processChatter, CHAT)

registerCommand(chatterControl, u"болталка", 30, 
				u"Отключает (0) или включает (1) болталку. Без параметра покажет текущее значение", 
				u"болталка [0|1]", 
				(u"болталка", u"болталка 0"), 
				CHAT)
