# coding: utf-8

# help.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Help Copyright (c) 2007 dimichxp <dimichxp@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showHelp(msgType, conference, nick, param):
	if param:
		command = param.lower()
		cmdType = isConferenceInList(conference) and CMD_CONFERENCE or CMD_ROSTER
		if isCommand(command) and isCommandType(command, cmdType):
			message = gCommands[command][CMD_DESC]
			syntax = gCommands[command][CMD_SYNTAX]
			if syntax:
				message += u"\nСинтаксис: %s %s" % (command, syntax)
			examples = gCommands[command][CMD_EXAMPLE]
			if examples:
				message += u"\nПримеры:"
				for example in examples:
					if example:
						message += u"\n * %s %s" % (command, example)
					else:
						message += u"\n * %s" % (command)
			if cmdType == CMD_CONFERENCE:
				message += u"\nМин. уровень доступа: %d" % (gCommands[command][CMD_ACCESS])
				if not isAvailableCommand(conference, command):
					message += u"\nЭта команда отключена в этой конференции!"
			sendMsg(msgType, conference, nick, message)
	else:
		if isConferenceInList(conference):
			prefix = getConferenceConfigKey(conference, "prefix")
		else:
			prefix = ""
		sendMsg(msgType, conference, nick, u"Напишите \"%sкоманды\", чтобы узнать список всех команд, \"%sпомощь <команда>\" для получения справки по использованию команды" % (prefix, prefix))

def showCommands(msgType, conference, nick, param):
	cmdType = isConferenceInList(conference) and CMD_CONFERENCE or CMD_ROSTER
	availableCmds, disabledCmds = [], []
	message = ""
	truejid = getTrueJID(conference, nick)
	for cmd in gCommands:
		if isCommandType(cmd, cmdType):
			if getAccess(conference, truejid) >= gCommands[cmd][CMD_ACCESS]:
				if cmdType == CMD_ROSTER:
					availableCmds.append(cmd)
				else:
					if isAvailableCommand(conference, cmd):
						availableCmds.append(cmd)
					else:
						disabledCmds.append(cmd)
	if availableCmds:
		availableCmds.sort()
		message += u"Доступные команды:\n%s" % (u", ".join(availableCmds))
	if disabledCmds:
		disabledCmds.sort()
		message += u"\n\nОтключенные команды:\n%s" % (", ".join(disabledCmds))
	if protocol.TYPE_PUBLIC == msgType:
		sendMsg(msgType, conference, nick, u"Ушли")
	sendMsg(protocol.TYPE_PRIVATE, conference, nick, message);	

registerCommand(showHelp, u"помощь", 0, 
				u"Показывает справку по использованию определённой команды, без параметра или выводит общую справку", 
				u"[команда]", 
				(None, u"пинг"), 
				CMD_ANY | CMD_FROZEN)
registerCommand(showCommands, u"команды", 0, 
				u"Показывает список доступных вам команд", 
				None, 
				None, 
				CMD_ANY | CMD_FROZEN | CMD_NONPARAM)
