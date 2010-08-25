# coding: utf-8;

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

CMDOFF_FILENAME = 'config/%s/cmdoff.txt';

def cmdSwitchOff(type, conference, nick, param):
	validCmd, invalidCmd, alreadySwitched, nonSwitched = [], [], [], [];
	message = u'';
	if(param):
		param = param.split();
		for cmd in param:
			if(isCommand(cmd) or gMacros.hasMacros(cmd, conference) or gMacros.hasMacros(cmd) and isCommandType(cmd, CHAT)):
				if(not isCommandType(cmd, FROZEN)):
					if(isAvailableCommand(conference, cmd)):
						gCmdOff[conference].append(cmd);
						validCmd.append(cmd);
					else:
						alreadySwitched.append(cmd);
				else:
					nonSwitched.append(cmd);
			else:
				invalidCmd.append(cmd);
		if(validCmd):
			validCmd.sort();
			message += u'были отключены следующие команды:\n' + ', '.join(validCmd);
		if(alreadySwitched):
			alreadySwitched.sort();
			message += u'\nследующие команды уже отключены:\n' + ', '.join(alreadySwitched);
		if(invalidCmd):
			invalidCmd.sort(); 
			message += u'\nперечисленное ниже не является командами:\n' + ', '.join(invalidCmd);
		if(nonSwitched):
			validCnonSwitchedmd.sort();
			message += u'\nследующие команды неотключаемы:\n' + ', '.join(nonSwitched);
		saveCommands(conference);
	else:
		validCmdReplic = [cmd for cmd in gCmdOff[conference]];
		if(validCmdReplic):
			message = u'в этой конференции отключены следующие команды:\n' + ', '.join(validCmdReplic);
		else:
			message = u'в этой конференции включены все команды';
	sendMsg(type, conference, nick, message);

registerCommand(cmdSwitchOff, u'комвыкл', 30, u'Отключает определённые команды для текущей конференции. Без параметров показывает список отключенных команд', u'комвыкл [команды]', (u'комвыкл', u'комвыкл тык диско версия пинг', ), CHAT | FROZEN);

def cmdSwitchOn(type, conference, nick, param):
	validCmd, invalidCmd, alreadySwitched = [], [], [];
	message = u'';
	param = param.split();
	for cmd in param:
		if(isCommand(cmd) or gMacros.hasMacros(cmd, conference) or gMacros.hasMacros(cmd) and isCommandType(cmd, CHAT)):
			if(not isAvailableCommand(conference, cmd)):
				gCmdOff[conference].remove(cmd);
				validCmd.append(cmd);
			else:
				alreadySwitched.append(cmd);
		else:
			invalidCmd.append(cmd);
	if(validCmd):
		validCmd.sort();
		message += u'были включены следующие команды:\n' + ', '.join(validCmd);
	if(alreadySwitched):
		alreadySwitched.sort();
		message += u'\nследующие команды уже включены:\n' + ', '.join(alreadySwitched);
	if(invalidCmd):
		invalidCmd.sort();
		message += u'\nперечисленное ниже не является командами:\n' + ', '.join(invalidCmd);
	saveCommands(conference);
	sendMsg(type, conference, nick, message);

registerCommand(cmdSwitchOn, u'комвкл', 30, u'Включает определённые команды для текущей конференции', u'комвкл <команды>', (u'комвкл тык диско версия пинг', ), CHAT | FROZEN | PARAM);

def saveCommands(conference):
	fileName = CMDOFF_FILENAME % (conference);
	writeFile(fileName, str(gCmdOff[conference]));

def loadCommands(conference):
	fileName = CMDOFF_FILENAME % (conference);
	createFile(fileName, '[]');
	gCmdOff[conference] = eval(readFile(fileName));

registerEvent(loadCommands, ADDCONF);

def unloadCommands(conference):
	del(gCmdOff[conference]);
	
registerEvent(unloadCommands, DELCONF);
