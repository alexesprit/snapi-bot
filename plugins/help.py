# coding: utf-8

# help.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Help Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) esprit

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
			buf = []
			
			buf.append(gCommands[command][CMD_DESC])
			buf.append("\n")
			syntax = gCommands[command][CMD_SYNTAX]
			if syntax:
				buf.append(u"Синтаксис: %s %s\n" % (command, syntax))
			examples = gCommands[command][CMD_EXAMPLE]
			if examples:
				buf.append(u"Примеры:\n")
				for example in examples:
					if example:
						buf.append(u" * %s %s\n" % (command, example))
					else:
						buf.append(u" * %s\n" % (command))
			if cmdType == CMD_CONFERENCE:
				buf.append(u"Мин. уровень доступа: %d\n" % (gCommands[command][CMD_ACCESS]))
				if not isAvailableCommand(conference, command):
					buf.append(u"Эта команда отключена в этой конференции!\n")
			sendMsg(msgType, conference, nick, "".join(buf))
	else:
		if isConferenceInList(conference):
			prefix = getConferenceConfigKey(conference, "prefix")
		else:
			prefix = ""
		sendMsg(msgType, conference, nick, u"Напишите \"%sкоманды\", чтобы узнать список всех команд, \"%sпомощь <команда>\" для получения справки по использованию команды" % (prefix, prefix))

def showCommands(msgType, conference, nick, param):
	availableCmds, disabledCmds = [], []
	buf = []

	cmdType = isConferenceInList(conference) and CMD_CONFERENCE or CMD_ROSTER
	truejid = getTrueJID(conference, nick)
	access = getAccess(conference, truejid)

	for cmd in gCommands:
		if isCommandType(cmd, cmdType):
			if gCommands[cmd][CMD_ACCESS] <= access:
				if cmdType == CMD_ROSTER:
					availableCmds.append(cmd)
				else:
					if isAvailableCommand(conference, cmd):
						availableCmds.append(cmd)
					else:
						disabledCmds.append(cmd)

	if availableCmds:
		availableCmds.sort()
		buf.append(u"Доступные команды (%d): %s\n\n" % (len(availableCmds), u", ".join(availableCmds)))

	if disabledCmds:
		disabledCmds.sort()
		buf.append(u"Отключенные команды (%d): %s\n" % (len(disabledCmds), ", ".join(disabledCmds)))

	if protocol.TYPE_PUBLIC == msgType:
		sendMsg(msgType, conference, nick, u"Ушли")
	sendMsg(protocol.TYPE_PRIVATE, conference, nick, "".join(buf))

registerCommand(showHelp, u"помощь", 0, 
				u"Показывает справку по использованию определённой команды. Без параметра или выводит общую справку",
				u"[команда]", 
				(None, u"пинг"), 
				CMD_ANY | CMD_FROZEN)
registerCommand(showCommands, u"команды", 0, 
				u"Показывает список доступных вам команд", 
				None, 
				None, 
				CMD_ANY | CMD_FROZEN | CMD_NONPARAM)
