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
	utils.createFile(path, "{}")
	gGreets[conference] = eval(utils.readFile(path))

def freeGreetings(conference):
	del gGreets[conference]

def setUserGreeting(msgType, conference, nick, param):
	rawGreet = param.split("=", 1)
	if len(rawGreet) == 2:
		user = rawGreet[0].strip()
		greet = rawGreet[1].strip()
		if isJid(user):
			trueJid = user
		elif nickInConference(user):
			trueJid = getTrueJid(conference, user)
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
		if not greet:
			if trueJid in gGreets[conference]:
				del gGreets[conference][trueJid]
		else:
			gGreets[conference][trueJid] = greet
		path = getConfigPath(conference, GREET_FILE)
		utils.writeFile(path, str(gGreets[conference]))
		sendMsg(msgType, conference, nick, u"Запомнила")

def sendUserGreeting(conference, nick, trueJid, aff, role):
	if trueJid in gGreets[conference]:
		sendMsg(protocol.TYPE_PUBLIC, conference, nick, gGreets[conference][trueJid])

registerEvent(loadGreetings, ADDCONF)
registerEvent(freeGreetings, DELCONF)
registerJoinHandler(sendUserGreeting)

registerCommand(setUserGreeting, u"приветствие", 30, 
				u"Добавляет приветствие для определённого ника/жида", 
				u"приветствие <ник|жид> = [текст]", 
				(u"приветствие Nick = something", ), 
				CHAT | PARAM)
