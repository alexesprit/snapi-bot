# coding: utf-8

# chatter.py
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

# chance 1 of N
SAVE_CHANCE = 25
REPLY_CHANCE = 35

CHATTERBOX_FILE = "chatter.txt"

gChatterCache = {}
gUpdateCount = {}

def setDefChatterValue(conference):
	if getConferenceConfigKey(conference, "chatter") is None:
		setConferenceConfigKey(conference, "chatter", 0)

def loadChatterBase(conference):
	path = getConfigPath(conference, CHATTERBOX_FILE)
	utils.createFile(path, "[]")
	gChatterCache[conference] = eval(utils.readFile(path))
	gUpdateCount[conference] = 0

def freeChatterBase(conference):
	del gChatterCache[conference]

def removeNicks(message, nickList):
	nickFound = False
	_startswith = message.startswith
	for nick in nickList:
		if _startswith(nick):
			for x in [nick + x for x in (":", ",")]:
				if _startswith(x):
					message = message.replace(x, "")
					nickFound = True
		if nickFound:
			break
	return message

def processChatter(stanza, msgType, conference, nick, truejid, message):
	if protocol.TYPE_PUBLIC == msgType and getConferenceConfigKey(conference, "chatter"):
		if not nick: # topic
			return
		botNick = getBotNick(conference)
		if nick == botNick:
			return

		isHiglight = message.startswith(botNick)

		if isHiglight or not random.randrange(0, REPLY_CHANCE):
			message = removeNicks(message, getNicks(conference)).strip()
			if message:
				command = message.split()[0].lower()
				_isCommand = isCommand(command) and isCommandType(command, CMD_CONFERENCE)
				_isMacros = gMacros.hasMacros(command, conference) or gMacros.hasMacros(command)
				if _isCommand or _isMacros:
					return
				if gChatterCache[conference]:
					text = random.choice(gChatterCache[conference])
					isMe = text.startswith("/me")
					time.sleep(len(text) / 4 + random.randrange(1, 5))
					if not isMe and (isHiglight or not random.randrange(0, 2)):
						sendMsg(msgType, conference, nick, text, True)
					else:
						sendToConference(conference, text)
		if isHiglight or not random.randrange(0, SAVE_CHANCE):
			message = removeNicks(message, getNicks(conference)).strip()
			if message:
				command = message.split()[0]
				if isCommand(command) or gMacros.hasMacros(command, conference) or gMacros.hasMacros(command):
					return
				if len(gChatterCache[conference]) >= MAX_MSG_COUNT:
					randNum = random.randrange(0, MAX_MSG_COUNT)
					del gChatterCache[conference][randNum]
				gChatterCache[conference].append(message)
				gUpdateCount[conference] += 1
				if gUpdateCount[conference] >= MSG_COUNT_TO_SAVE:
					path = getConfigPath(conference, CHATTERBOX_FILE)
					utils.writeFile(path, str(gChatterCache[conference]))
					gUpdateCount[conference] = 0

def manageChatterValue(msgType, conference, nick, param):
	if param:
		if param.isdigit():
			param = int(param)
			if param == 1:
				setConferenceConfigKey(conference, "chatter", 1)
				sendMsg(msgType, conference, nick, u"Болталка включена")
			else:
				setConferenceConfigKey(conference, "chatter", 0)
				sendMsg(msgType, conference, nick, u"Болталка отключена")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"Прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"Текущее значение: %d" % (getConferenceConfigKey(conference, "chatter")))

registerEventHandler(loadChatterBase, EVT_ADDCONFERENCE)
registerEventHandler(freeChatterBase, EVT_DELCONFERENCE)
registerEventHandler(setDefChatterValue, EVT_ADDCONFERENCE)

registerEventHandler(processChatter, EVT_MSG | H_CONFERENCE)

registerCommand(manageChatterValue, u"болталка", 30, 
				u"Отключает (0) или включает (1) болталку. Без параметра покажет текущее значение", 
				u"[0|1]", 
				(None, u"0"), 
				CMD_CONFERENCE)
