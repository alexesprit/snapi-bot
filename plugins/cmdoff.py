# coding: utf-8

# cmdoff.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CMDOFF_FILE = "cmdoff.dat"

def loadDisabledCommands(conference):
	path = getConfigPath(conference, CMDOFF_FILE)
	gCmdOff[conference] = io.load(path, [])

def freeDisableCommands(conference):
	del gCmdOff[conference]

def saveDisabledCommands(conference):
	path = getConfigPath(conference, CMDOFF_FILE)
	io.dump(path, gCmdOff[conference])

def disableCommand(msgType, conference, nick, param):
	if param:
		validCmd, invalidCmd, alreadySwitched, nonSwitched = [], [], [], []
		buf = []

		args = param.split()
		for cmd in args:
			_isCommand = isCommand(cmd) and isCommandType(cmd, CMD_CONFERENCE)
			_isMacros = isMacros(cmd, conference)
			if _isCommand or _isMacros:
				if _isMacros or not isCommandType(cmd, CMD_FROZEN):
					if isAvailableCommand(conference, cmd):
						gCmdOff[conference].append(cmd)
						validCmd.append(cmd)
					else:
						alreadySwitched.append(cmd)
				else:
					nonSwitched.append(cmd)
			else:
				invalidCmd.append(cmd)
		saveDisabledCommands(conference)

		if validCmd:
			validCmd.sort()
			buf.append(u"Отключены: %s\n" % (", ".join(validCmd)))
		if alreadySwitched:
			alreadySwitched.sort()
			buf.append(u"Уже отключены: %s\n" % (", ".join(alreadySwitched)))
		if nonSwitched:
			nonSwitched.sort()
			buf.append(u"Неотключаемы: %s\n" % (", ".join(nonSwitched)))
		if invalidCmd:
			invalidCmd.sort()
			buf.append(u"Не являются командами/макросами: %s\n" % (", ".join(invalidCmd)))
		sendMsg(msgType, conference, nick, "".join(buf))
	else:
		buf = []
		commandsOff = [cmd for cmd in gCmdOff[conference] if isCommand(cmd)]
		macrosesOff = [cmd for cmd in gCmdOff[conference] if isMacros(cmd, conference)]
		if commandsOff:
			commandsOff.sort()
			buf.append(u"Отключены следующие команды: %s\n" % (", ".join(commandsOff)))
		if macrosesOff:
			macrosesOff.sort()
			buf.append(u"Отключены следующие макросы: %s\n" % (", ".join(macrosesOff)))
		if buf:
			sendMsg(msgType, conference, nick, "".join(buf))
		else:
			sendMsg(msgType, conference, nick, u"В этой конференции включены все команды/макросы")

def enableCommand(msgType, conference, nick, param):
	validCmd, invalidCmd, alreadySwitched = [], [], []
	buf = []

	args = param.split()
	for cmd in args:
		_isCommand = isCommand(cmd) and isCommandType(cmd, CMD_CONFERENCE)
		_isMacros = isMacros(cmd, conference)
		if _isCommand or _isMacros:
			if not isAvailableCommand(conference, cmd):
				gCmdOff[conference].remove(cmd)
				validCmd.append(cmd)
			else:
				alreadySwitched.append(cmd)
		else:
			invalidCmd.append(cmd)
	saveDisabledCommands(conference)

	if validCmd:
		validCmd.sort()
		buf.append(u"Включены: %s\n" % (", ".join(validCmd)))
	if alreadySwitched:
		alreadySwitched.sort()
		buf.append(u"Уже включены: %s\n" % (", ".join(alreadySwitched)))
	if invalidCmd:
		invalidCmd.sort()
		buf.append(u"Не являются командами/макросами: %s\n" % (", ".join(invalidCmd)))
	sendMsg(msgType, conference, nick, "".join(buf))

registerEventHandler(loadDisabledCommands, EVT_ADDCONFERENCE)
registerEventHandler(freeDisableCommands, EVT_DELCONFERENCE)

registerCommand(enableCommand, u"комвкл", 30,
				u"Включает определённые команды/макросы для текущей конференции",
				u"<команды>",
				(u"тык диско версия пинг", ),
				CMD_CONFERENCE | CMD_FROZEN | CMD_PARAM)
registerCommand(disableCommand, u"комвыкл", 30,
				u"Отключает определённые команды/макросы для текущей конференции. Без параметров показывает список отключенных команд/макросов",
				u"[команды]",
				(None, u"тык диско версия пинг", ),
				CMD_CONFERENCE | CMD_FROZEN)
