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
	utils.createFile(path, "[]")
	gCmdOff[conference] = eval(utils.readFile(path))

def freeDisableCommands(conference):
	del gCmdOff[conference]

def saveDisabledCommands(conference):
	path = getConfigPath(conference, CMDOFF_FILE)
	utils.writeFile(path, str(gCmdOff[conference]))

def disableCommand(msgType, conference, nick, param):
	if param:
		validCmd, invalidCmd, alreadySwitched, nonSwitched = [], [], [], []
		message = u""
		param = param.split()
		for cmd in param:
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
		if validCmd:
			validCmd.sort()
			message += u"Были отключены:\n * %s" % (", ".join(validCmd))
		if alreadySwitched:
			alreadySwitched.sort()
			message += u"\nУже отключены:\n * %s" % (", ".join(alreadySwitched))
		if invalidCmd:
			invalidCmd.sort()
			message += u"\nНе являются командами:\n * %s" % (", ".join(invalidCmd))
		if nonSwitched:
			nonSwitched.sort()
			message += u"\nНеотключаемы:\n * %s" % (", ".join(nonSwitched))
		saveDisabledCommands(conference)
	else:
		switchedOn = [cmd for cmd in gCmdOff[conference]]
		if switchedOn:
			message = u"Отключены следующие команды:\n * %s" % (", ".join(switchedOn))
		else:
			message = u"В этой конференции включены все команды"
	sendMsg(msgType, conference, nick, message)

def enableCommand(msgType, conference, nick, param):
	validCmd, invalidCmd, alreadySwitched = [], [], []
	message = u""
	param = param.split()
	for cmd in param:
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
	if validCmd:
		validCmd.sort()
		message += u"Были включены:\n * %s" % (", ".join(validCmd))
	if alreadySwitched:
		alreadySwitched.sort()
		message += u"\nУже включены:\n * %s" % (", ".join(alreadySwitched))
	if invalidCmd:
		invalidCmd.sort()
		message += u"\nпНе являются командами:\n * %s" % (", ".join(invalidCmd))
	saveDisabledCommands(conference)
	sendMsg(msgType, conference, nick, message)

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
