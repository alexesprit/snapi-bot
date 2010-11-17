# coding: utf-8

# botversion.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VER_FILE = "version.txt"

def setBotVersion(msgType, conference, nick, param):
	global gVersion
	if not param:
		sendMsg(msgType, conference, nick, u"|".join(gVersion))
	elif param.count("|") == 2:
		gVersion = tuple(param.split("|"))
		path = getConfigPath(VER_FILE)
		utils.writeFile(path, str(gVersion))
		sendMsg(msgType, conference, nick, u"Поняла, сейчас поставлю")
	else:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")

def loadBotVersion():
	global gVersion
	path = getConfigPath(VER_FILE)
	utils.createFile(path, str(gVersion))
	gVersion = eval(utils.readFile(path))

registerEvent(loadBotVersion, STARTUP)

registerCommand(setBotVersion, u"ботверсия", 100, 
				u"Выставляет версию клиента у бота. Без параметра покажет текущее значение", 
				u"[клиент|версия|ось]", 
				(None, u"Jimm|0.6.4|Nokia 3310"), 
				ROSTER)
