# coding: utf-8;

# macros.py 
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def addLocalMacros(msgType, conference, nick, param):
	rawMacros = param.split('=', 1);
	if(len(rawMacros) != 2):
		sendMsg(msgType, conference, nick, u'читай справку по команде');
		return;
	else:
		macros, body = rawMacros;
		macros = macros.strip();
		body = body.strip();
	if(macros and body):
		if(isCommand(macros)):
			sendMsg(msgType, conference, nick, u'это имя уже занято командой');
		elif(gMacros.hasMacros(macros)):
			sendMsg(msgType, conference, nick, u'не могу, глобальный макрос есть такой :(');
		else:
			command = body.split()[0];
			if(isCommand(command)):
				access = gCommands[command][CMD_ACCESS];
			elif(gMacros.hasMacros(command)):
				access = gMacros.getAccess(command);
			elif(gMacros.hasMacros(command, conference)):
				access = gMacros.getAccess(command, conference);
			else:
				sendMsg(msgType, conference, nick, u'не вижу команду внутри макроса');
				return;
			trueJid = getTrueJid(conference, nick);
			if(getAccess(conference, trueJid) >= access):
				if(gMacros.hasMacros(macros, conference)):
					sendMsg(msgType, conference, nick, u'заменила');
				else:
					sendMsg(msgType, conference, nick, u'добавила');		
				gMacros.add(macros, body, access, conference);
				gMacros.saveMacroses(conference);
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'читай справку по команде');

registerCommand(addLocalMacros, u'макроадд', 20, u'Добавить макрос', u'макроадд <название>=<макрос>', (u'макроадд глюк=сказать /me подумал, что все глючат', ), CHAT | PARAM);

def addGlobalMacros(msgType, conference, nick, param):
	rawMacros = param.split('=', 1);
	if(len(rawMacros) != 2):
		sendMsg(msgType, conference, nick, u'читай справку по команде');
		return;
	else:
		macros, body = rawMacros;
		macros = macros.strip();
		body = body.strip();
	if(macros and body):
		if(isCommand(macros)):
			sendMsg(msgType, conference, nick, u'это имя уже занято командой');
		else:
			command = body.split()[0];
			if(isCommand(command)):
				access = gCommands[command][CMD_ACCESS];
			elif(gMacros.hasMacros(command)):
				access = gMacros.getAccess(command);
			else:
				sendMsg(msgType, conference, nick, u'не вижу команду внутри макроса');
				return;
			if(gMacros.hasMacros(macros)):
				access = gMacros.getAccess(macros);
				sendMsg(msgType, conference, nick, u'заменила');
			else:
				sendMsg(msgType, conference, nick, u'добавила');
			gMacros.add(macros, body, access);
			gMacros.saveMacroses();
	else:
		sendMsg(msgType, conference, nick, u'читай справку по команде');

registerCommand(addGlobalMacros, u'гмакроадд', 100, u'Добавить глобальный макрос', u'гмакроадд <название>=<макрос>', (u'гмакроадд глюк=сказать /me подумал, что все глючат', ), ANY | PARAM);

def delLocalMacros(msgType, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			gMacros.remove(param, conference);
			gMacros.saveMacroses(conference);
			sendMsg(msgType, conference, nick, u'удалила');
		else:
			sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(delLocalMacros, u'макродел', 20, u'Удалить макроc', u'макродел <название>', (u'макродел глюк', ), CHAT);

def delGlobalMacros(msgType, conference, nick, param):
	if(gMacros.hasMacros(param)): 
		gMacros.remove(param);
		gMacros.saveMacroses();
		sendMsg(msgType, conference, nick, u'убила');
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(delGlobalMacros, u'гмакродел', 100, u'Удалить глобальный макроc', u'ггмакродел <название>', (u'гмакродел глюк', ), ANY | PARAM);

def expandLocalMacros(msgType, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			sendMsg(msgType, conference, nick, gMacros.expand(param, (conference, nick, ), conference));
		else:
			sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(expandLocalMacros, u'макроэксп', 20, u'Развернуть макроc, т.е. посмотреть на него в сыром виде', u'макроэксп <название> [параметры]', (u'макроэксп админ бот', ), CHAT);

def expandGlobalMacros(msgType, conference, nick, param):
	macros = param.split()[0].lower();
	if(gMacros.hasMacros(macros)):
		sendMsg(msgType, conference, nick, gMacros.expand(param, (conference, nick, )));
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(expandGlobalMacros, u'гмакроэксп', 100, u'Развернуть макроc, т.е. посмотреть на него в сыром виде', u'гмакроэксп <название> [параметры]', (u'гмакроэксп админ бот', ), ANY | PARAM);

def showLocalMacrosInfo(msgType, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			sendMsg(msgType, conference, nick, gMacros.getMacros(param, conference));
		else:
			sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(showLocalMacrosInfo, u'макроинфо', 20, u'Открыть макрос, т.е. просто посмотреть как он выглядит', u'макроинфо [название]', (u'макроинфо глюк', ), CHAT);

def showGlobalMacrosInfo(msgType, conference, nick, param):
	param = param.lower();
	if(gMacros.hasMacros(param)):
		sendMsg(msgType, conference, nick, gMacros.getMacros(param));
	else:
		sendMsg(msgType, conference, nick, u'нет такого макроса');

registerCommand(showGlobalMacrosInfo, u'гмакроинфо', 100, u'Открыть глобальный макрос, т.е. просто посмотреть как он выглядит', u'гмакроинфо [название]', (u'гмакроинфо глюк', ), ANY | PARAM);

def showLocalMacroAccess(msgType, conference, nick, param):
	param = param.split();
	macros = param[0];
	if(gMacros.hasMacros(macros, conference)):
		if(len(param) == 2):
			access = gMacros.getAccess(macros, conference);
			trueJid = getTrueJid(conference, nick);
			if(getAccess(conference, trueJid) >= access):
				access = param[1];
				if(access.isdigit()):
					access = int(param[1]);
					gMacros.setAccess(macros, access, conference);
					gMacros.saveMacroses(conference);
					sendMsg(msgType, conference, nick, u'дала');
				else:
					sendMsg(msgType, conference, nick, u'ошибочный запрос');
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');
		elif(len(param) == 1):
			access = gMacros.getAccess(macros, conference);
			sendMsg(msgType, conference, nick, str(access));
		else:
			sendMsg(msgType, conference, nick, u'ошибочный запрос');
	else:
		sendMsg(msgType, conference, nick, u'нету такого макроса');

registerCommand(showLocalMacroAccess, u'макродоступ', 20, u'Изменить или посмотреть доступ к макросу', u'макродоступ <название> [доступ]', (u'макродоступ глюк 10', u'макродоступ глюк'), CHAT | PARAM);

def showGlobalMacroAccess(msgType, conference, nick, param):
	param = param.split();
	macros = param[0];
	if(gMacros.hasMacros(macros)):
		if(len(param) == 2):
			access = param[1];
			if(access.isdigit()):
				access = int(param[1]);
				gMacros.setAccess(macros, access);
				gMacros.saveMacroses();
				sendMsg(msgType, conference, nick, u'дала');
			else:
				sendMsg(msgType, conference, nick, u'ошибочный запрос');
		elif(len(param) == 1):
			access = gMacros.getAccess(macros);
			sendMsg(msgType, conference, nick, str(access));
		else:
			sendMsg(msgType, conference, nick, u'ошибочный запрос');
	else:
		sendMsg(msgType, conference, nick, u'нету такого макроса');

registerCommand(showGlobalMacroAccess, u'гмакродоступ', 100, u'Изменить или посмотреть доступ к глобальному макросу', u'гмакродоступ <название> [доступ]', (u'гмакродоступ админ 20', u'гмакродоступ админ'), ANY | PARAM);

def showMacrosList(msgType, conference, nick, parameters):
	message, disMacroses, macroses = u'', [], [];
	trueJid = getTrueJid(conference, nick);
	isConference = conferenceInList(conference);
	if(isConference):
		for macros in gMacros.getMacrosList(conference):
			if(isAvailableCommand(conference, macros)):
				access = gMacros.getAccess(macros, conference);
				if(getAccess(conference, trueJid) >= access):
					macroses.append(macros);
			else:
				disMacroses.append(macros);
		if(macroses):
			macroses.sort();
			message += u'Локальные:\n'+', '.join(macroses) + '\n';
		if(disMacroses):
			disMacroses.sort();
			message += u'Отключённые локальные макросы:\n' + ', '.join(disMacroses) + '\n\n';
		macroses = [];
		disMacroses = [];	
	for macros in gMacros.getMacrosList():
		if(isConference):
			if(isAvailableCommand(conference, macros)):
				access = gMacros.getAccess(macros);
				if(getAccess(conference, trueJid) >= access):
					macroses.append(macros);
			else:
				disMacroses.append(macros);
		else:
			macroses.append(macros);
	if(macroses):
		macroses.sort();
		message += u'Глобальные:\n' + ', '.join(macroses);
	if(isConference):
		if(disMacroses):
			disMacroses.sort();
			message += u'\nОтключённые глобальные макросы:\n' + ', '.join(disMacroses);
	if(message):
		if(msgType == xmpp.TYPE_PUBLIC):
			sendMsg(msgType, conference, nick, u'ушёл');
		sendMsg(xmpp.TYPE_PRIVATE, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u'нету макросов :(');

registerCommand(showMacrosList, u'макролист', 10, u'Список макросов', None, (u'макролист', ), ANY | NONPARAM);

def loadMacroses(conference):
	gMacros.loadMacroses(conference);

registerEvent(loadMacroses, ADDCONF);

def unloadMacroses(conference):
	gMacros.unloadMacroses(conference);

registerEvent(unloadMacroses, DELCONF);
	
def loadGlobalMacroses():
	gMacros.loadMacroses();

registerEvent(loadGlobalMacroses, STARTUP);
