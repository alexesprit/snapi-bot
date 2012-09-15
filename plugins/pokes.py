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

def pokeUser(msgType, conference, nick, param):
	if msgType == protocol.TYPE_PUBLIC:
		if param:
			pokesPath = getFilePath(RESOURCE_DIR, POKES_FILE)
			pokes = eval(io.read(pokesPath))

			botNick = getBotNick(conference)
			if param == u"всех":
				for userNick in getOnlineNicks(conference):
					if userNick != botNick and userNick != nick:
						sendToConference(conference, random.choice(pokes) % (userNick))
						time.sleep(0.5)
			elif isNickOnline(conference, param):
				if param == botNick:
					param = nick
				sendToConference(conference, random.choice(pokes) % (param))
			else:
				sendMsg(msgType, conference, nick, u"А это кто?")
		else:
			sendMsg(msgType, conference, nick, u"Мазохист? :D")
	else:
		sendMsg(msgType, conference, nick, u":-P")

registerCommand(pokeUser, u"тык", 10, 
				u"Тыкает пользователя. Заставляет его обратить внимание на вас", 
				u"<ник>", 
				(u"Nick", ), 
				CMD_CONFERENCE);
