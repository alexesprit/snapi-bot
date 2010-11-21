# coding: utf-8;

# commands.py
# Initial Copyright (c) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CMDACCESS_FILE = 'cmdaccess.txt'

def saveCommandAccesses():
	global gCommandAccess
	path = getConfigPath(CMDACCESS_FILE)
	utils.writeFile(path, str(gCommandAccess))

def loadCommandAccesses():
	global gCommandAccess
	path = getConfigPath(CMDACCESS_FILE)
	utils.createFile(path, '{}')
	gCommandAccess = eval(utils.readFile(path))
	for command in gCommandAccess:
		gCommands[command][CMD_ACCESS] = gCommandAccess[command]

def changeCommandAccess(msgType, conference, nick, param):
	param = param.split()
	if len(param) == 2:
		command = param[0]
		access = param[1]
		if isCommand(command):
			if access.isdigit() and -100 <= int(access) <= 100:
				access = int(access)
				gCommandAccess[command] = access
				gCommands[command][CMD_ACCESS] = access
				saveCommandAccesses()
				sendMsg(msgType, conference, nick, u'запомнила')
			else:
				sendMsg(msgType, conference, nick, u'ошибочный запрос')
				return
		else:
			sendMsg(msgType, conference, nick, u'не вижу команду')
	else:
		sendMsg(msgType, conference, nick, u'читай справку по команде')

registerEvent(loadCommandAccesses, EVT_STARTUP)
registerCommand(changeCommandAccess, 
				u'командоступ', 100, 
				u'Меняет доступ для команды', 
				u'<команда> <число>', 
				(u'пинг 100', ), 
				CMD_ANY | CMD_PARAM)
