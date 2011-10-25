# coding: utf-8

# cmdoff.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CMDOFF_FILE = "cmdoff.txt"

def loadDisabledCommands(conference):
	path = getConfigPath(conference, CMDOFF_FILE)
	gCmdOff[conference] = eval(utils.readFile(path, "[]"))

def freeDisableCommands(conference):
	del gCmdOff[conference]

def saveDisabledCommands(conference):
	path = getConfigPath(conference, CMDOFF_FILE)
	utils.writeFile(path, str(gCmdOff[conference]))

def disableCommand(msgType, conference, nick, param):
	if param:
		validCmd, invalidCmd, alreadySwitched, nonSwitched = [], [], [], []
		buf = []

		args = param.split()
		for cmd in args:
			_isCommand = isCommand(cmd) and isCommandType(cmd, CMD_CONFERENCE)
			_isMacros = gMacros.hasMacros(cmd, conference) or gMacros.hasMacros(cmd)
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
			buf.append(u"Не являются командами: %s\n" % (", ".join(invalidCmd)))
		sendMsg(msgType, conference, nick, "".join(buf))
	else:
		switchedOn = [cmd for cmd in gCmdOff[conference]]
		if switchedOn:
			sendMsg(msgType, conference, nick,
				u"Отключены следующие команды: %s" % (", ".join(switchedOn)))
		else:
			sendMsg(msgType, conference, nick, u"В этой конференции включены все команды")

def enableCommand(msgType, conference, nick, param):
	validCmd, invalidCmd, alreadySwitched = [], [], []
	buf = []

	args = param.split()
	for cmd in args:
		_isCommand = isCommand(cmd) and isCommandType(cmd, CMD_CONFERENCE)
		_isMacros = gMacros.hasMacros(cmd, conference) or gMacros.hasMacros(cmd)
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
		buf.append(u"Не являются командами: %s\n" % (", ".join(invalidCmd)))
	sendMsg(msgType, conference, nick, "".join(buf))

registerEventHandler(loadDisabledCommands, EVT_ADDCONFERENCE)
registerEventHandler(freeDisableCommands, EVT_DELCONFERENCE)

registerCommand(enableCommand, u"комвкл", 30,
				u"Включает определённые команды для текущей конференции",
				u"<команды>",
				(u"тык диско версия пинг", ),
				CMD_CONFERENCE | CMD_FROZEN | CMD_PARAM)
registerCommand(disableCommand, u"комвыкл", 30,
				u"Отключает определённые команды для текущей конференции. Без параметров показывает список отключенных команд",
				u"[команды]",
				(None, u"тык диско версия пинг", ),
				CMD_CONFERENCE | CMD_FROZEN)
