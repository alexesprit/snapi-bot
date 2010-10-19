# coding: utf-8

# jokes.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

JOKES_FILE = "jokes.txt"

def loadJokes():
	global gJokes
	fileName = util.getFilePath(RESOURCE_DIR, JOKES_FILE)
	gJokes = eval(util.readFile(fileName, "utf-8"))

def setDefJokesValue(conference):
	if(getConfigKey(conference, "jokes") is None):
		setConfigKey(conference, "jokes", 1)

def manageJokesValue(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param == 1):
				setConfigKey(conference, "jokes", 1)
				sendMsg(msgType, conference, nick, u"шуточки включены")
			else:
				setConfigKey(conference, "jokes", 0)
				sendMsg(msgType, conference, nick, u"шуточки отключены")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"прочитай помощь по команде")
	else:
		jokesValue = getConfigKey(conference, "jokes")
		sendMsg(msgType, conference, nick, u"текущее значение: %d" % (jokesValue))

registerEvent(loadJokes, STARTUP)
registerEvent(setDefJokesValue, ADDCONF)

registerCommand(manageJokesValue, u"шуточки", 30, 
				u"Отключает (0) или включает (1) шуточки, которыми бот порою подменяет ответ. Без параметра покажет текущее значение", 
				u"шуточки [0|1]", 
				(u"шуточки", u"шуточки 0"), 
				CHAT)
