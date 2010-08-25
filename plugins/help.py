# coding: utf-8;

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

def showHelp(type, conference, nick, param):
	if(param):
		param = param.lower();
		cmdType = conferenceInList(conference) and CHAT or ROSTER;
		if(isCommand(param) and isCommandType(param, cmdType)):
			message = gCommands[param]['desc'];
			syntax = gCommands[param]['syntax'];
			if(syntax):
				message += u'\nСинтаксис: %s' % (gCommands[param]['syntax']);
			message += u'\nПримеры:'
			for example in gCommands[param]['examples']:
				message += u'\n * %s' % (example);
			if(cmdType == CHAT):
				message += u'\nМин. уровень доступа: %d' % (gCommands[param]['access']);
				if(not isAvailableCommand(conference, param)):
					message += u'\nЭта команда отключена в этой конференции!';
			sendMsg(type, conference, nick, message);
	else:
		if(conferenceInList(conference)):
			prefix = getConfigKey(conference, 'prefix') or '';
		else:
			prefix = '';
		sendMsg(type, conference, nick, u'напишите "%sкоманды", чтобы узнать список всех команд, "%sпомощь <команда>" для получения справки по использованию команды' % (prefix, prefix));

def showCommands(type, conference, nick, param):
	cmdType = conferenceInList(conference) and CHAT or ROSTER;
	availableCmds, disabledCmds = [], [];
	message = '';
	trueJid = getTrueJid(conference, nick);
	for cmd in gCommands:
		if(isCommandType(cmd, cmdType)):
			if(getAccess(conference, trueJid) >= gCommands[cmd]['access']):
				if(cmdType == ROSTER):
					availableCmds.append(cmd);
				else:
					if(isAvailableCommand(conference, cmd)):
						availableCmds.append(cmd);
					else:
						disabledCmds.append(cmd);
	if(availableCmds):
		availableCmds.sort();
		message += u'Доступные команды:\n%s' % (u', '.join(availableCmds));
	if(disabledCmds):
		disabledCmds.sort();
		message += u'\n\nОтключенные команды:\n%s' % (', '.join(disabledCmds));
	if(PUBLIC == type):
		sendMsg(type, conference, nick, u'ушли');
	sendMsg(PRIVATE, conference, nick, message);	

registerCommand(showHelp, u'помощь', 0, u'Даёт справку об определённой команде или выводит общую справку', u'помощь [команда]', (u'помощь', u'помощь пинг'), ANY | FROZEN);
registerCommand(showCommands, u'команды', 0, u'Показывает список всех команд', None, (u'команды', ), ANY | FROZEN | NONPARAM);
