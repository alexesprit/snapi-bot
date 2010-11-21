# coding: utf-8

# pokes.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

POKES_FILE = "pokes.txt"

gPokes = []

def loadPokes():
	global gPokes
	path = getFilePath(RESOURCE_DIR, POKES_FILE)
	gPokes = eval(utils.readFile(path, "utf-8"))

def pokeUser(msgType, conference, nick, param):
	if msgType == protocol.TYPE_PUBLIC:
		if param:
			botNick = getBotNick(conference)
			if param == u"всех":
				for userNick in getOnlineNicks(conference):
					if userNick != botNick and userNick != nick:
						message = random.choice(gPokes)
						sendToConference(conference, u"/me " + message % (userNick))
						time.sleep(0.5)
			elif isNickOnline(conference, param):
				if param == botNick:
					param = nick
				message = random.choice(gPokes)
				sendToConference(conference, u"/me " + message % (param))
			else:
				sendMsg(msgType, conference, nick, u"А это кто?")
		else:
			sendMsg(msgType, conference, nick, u"Мазохист? :D")
	else:
		sendMsg(msgType, conference, nick, u":-P")

registerEvent(loadPokes, EVT_STARTUP)

registerCommand(pokeUser, u"тык", 10, 
				u"Тыкает пользователя. Заставляет его обратить внимание на вас", 
				u"<ник>", 
				(u"Nick", ), 
				CMD_CONFERENCE);
