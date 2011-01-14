# coding: utf-8

# greets.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

GREET_FILE = "greets.txt"

gGreets = {}

def loadGreetings(conference):
	path = getConfigPath(conference, GREET_FILE)
	gGreets[conference] = eval(utils.readFile(path, "{}"))

def freeGreetings(conference):
	del gGreets[conference]

def setUserGreeting(msgType, conference, nick, param):
	rawGreet = param.split("=", 1)
	if len(rawGreet) == 2:
		user = rawGreet[0].strip()
		greet = rawGreet[1].strip()
		if isJID(user):
			truejid = user
		elif isNickInConference(conference, user):
			truejid = getTrueJID(conference, user)
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
		if not greet:
			if truejid in gGreets[conference]:
				del gGreets[conference][truejid]
		else:
			gGreets[conference][truejid] = greet
		path = getConfigPath(conference, GREET_FILE)
		utils.writeFile(path, str(gGreets[conference]))
		sendMsg(msgType, conference, nick, u"Запомнила")

def sendGreetingToUser(conference, nick, truejid, aff, role):
	if truejid in gGreets[conference]:
		sendMsg(protocol.TYPE_PUBLIC, conference, nick, gGreets[conference][truejid])

registerEventHandler(loadGreetings, EVT_ADDCONFERENCE)
registerEventHandler(freeGreetings, EVT_DELCONFERENCE)

registerEventHandler(sendGreetingToUser, EVT_USERJOIN)

registerCommand(setUserGreeting, u"приветствие", 30, 
				u"Устанавливает приветствие для определённого ника/жида",
				u"<ник|жид> = [текст]", 
				(u"Nick = Привет!", u"user@server.tld = Привет!"), 
				CMD_CONFERENCE | CMD_PARAM)
