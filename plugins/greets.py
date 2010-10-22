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
	fileName = getConfigPath(conference, GREET_FILE)
	utils.createFile(fileName, "{}")
	gGreets[conference] = eval(utils.readFile(fileName))

def freeGreetings(conference):
	del(gGreets[conference])

def setUserGreeting(msgType, conference, nick, param):
	rawGreet = param.split("=", 1)
	if(len(rawGreet) == 2):
		userNick = rawGreet[0].strip()
		greet = rawGreet[1].strip()
		if(userNick.count("@")):
			trueJid = userNick
		elif(userNick in getNicks(conference)):
			trueJid = getTrueJid(conference, userNick)
		else:
			sendMsg(msgType, conference, nick, u"а это кто?")
			return
		if(not greet):
			if(trueJid in gGreets[conference]):
				del(gGreets[conference][trueJid])
		else:
			gGreets[conference][trueJid] = greet
		fileName = getConfigPath(conference, GREET_FILE)
		utils.writeFile(fileName, str(gGreets[conference]))
		sendMsg(msgType, conference, nick, u"запомнила")

def sendUserGreeting(conference, nick, trueJid, aff, role):
	if(trueJid in gGreets[conference]):
		sendMsg(protocol.TYPE_PUBLIC, conference, nick, gGreets[conference][trueJid])

registerEvent(loadGreetings, ADDCONF)
registerEvent(freeGreetings, DELCONF)
registerJoinHandler(sendUserGreeting)

registerCommand(setUserGreeting, u"приветствие", 30, 
				u"Добавляет приветствие для определённого ника/жида", 
				u"приветствие <ник|жид> = [текст]", 
				(u"приветствие Nick = something", ), 
				CHAT | PARAM)
