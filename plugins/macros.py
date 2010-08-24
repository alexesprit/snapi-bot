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

def addLocalMacros(type, conference, nick, param):
	macros = param.split()[0].lower();
	if(isCommand(macros)):
		sendMsg(type, conference, nick, u'это имя уже занято командой');
	elif(gMacros.hasMacros(macros)):
		sendMsg(type, conference, nick, u'не могу, глобальный макрос есть такой :(');
	else:
		raw = gMacros.parseCommand(param);
		if(len(raw) < 2):
			sendMsg(type, conference, nick, u'мало аргументов');
			return;
		command = raw[1].split()[0];
		if(isCommand(command)):
			access = gCommands[command]['access'];
		elif(gMacros.hasMacros(command)):
			access = gMacros.getAccess(command);
		elif(gMacros.hasMacros(command, conference)):
			access = gMacros.getAccess(command, conference);
		else:
			sendMsg(type, conference, nick, u'не вижу команду внутри макроса');
			return;
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			if(gMacros.hasMacros(macros, conference)):
				sendMsg(type, conference, nick, u'заменила');
			else:
				sendMsg(type, conference, nick, u'добавила');		
			gMacros.add(raw[0], raw[1], access, conference);
			gMacros.saveMacroses(conference);
		else:
			sendMsg(type, conference, nick, u'недостаточно прав');

registerCommandHandler(addLocalMacros, u'макроадд', 20, u'Добавить макрос. Тело макроса должно быть заключено в апострофы (`)', u'макроадд <название> `<макрос>`', (u'макроадд глюк `сказать /me подумал, что все глючат`', ), ANY | PARAM);

def addGlobalMacros(type, conference, nick, param):
	macros = param.split()[0].lower();
	if(isCommand(macros)):
		sendMsg(type, conference, nick, u'это имя уже занято командой');
	else:
		raw = gMacros.parseCommand(param);
		if(len(raw) < 2):
			sendMsg(type, conference, nick, u'мало аргументов');
			return;
		command = raw[1].split()[0];
		if(isCommand(command)):
			access = gCommands[command]['access'];
		elif(gMacros.hasMacros(command)):
			access = gMacros.getAccess(command);
		else:
			sendMsg(type, conference, nick, u'не вижу команду внутри макроса');
			return;
		if(gMacros.hasMacros(macros)):
			sendMsg(type, conference, nick, u'заменила');
		else:
			sendMsg(type, conference, nick, u'добавила');
		gMacros.add(raw[0], raw[1], access);
		gMacros.saveMacroses();

registerCommandHandler(addGlobalMacros, u'гмакроадд', 100, u'Добавить глобальный макрос. Тело макроса должно быть заключено в апострофы (`)', u'гмакроадд <название> `<макрос>`', (u'гмакроадд глюк `сказать /me подумал, что все глючат`', ), ANY | PARAM);

def delLocalMacros(type, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			gMacros.remove(param, conference);
			gMacros.saveMacroses(conference);
			sendMsg(type, conference, nick, u'удалила');
		else:
			sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def delGlobalMacros(type, conference, nick, param):
	if(gMacros.hasMacros(param)): 
		gMacros.remove(param);
		gMacros.saveMacroses();
		sendMsg(type, conference, nick, u'убила');
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def expandLocalMacros(type, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			sendMsg(type, conference, nick, gMacros.expand(param, (conference, nick, ), conference));
		else:
			sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def expandGlobalMacros(type, conference, nick, param):
	macros = param.split()[0].lower();
	if(gMacros.hasMacros(macros)):
		sendMsg(type, conference, nick, gMacros.expand(param, (conference, nick, )));
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def showLocalMacrosInfo(type, conference, nick, param):
	if(gMacros.hasMacros(param, conference)):
		access = gMacros.getAccess(macros, conference);
		trueJid = getTrueJid(conference, nick);
		if(getAccess(conference, trueJid) >= access):
			sendMsg(type, conference, nick, gMacros.getMacros(param, conference));
		else:
			sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def showGlobalMacrosInfo(type, conference, nick, param):
	param = param.lower();
	if(gMacros.hasMacros(param)):
		sendMsg(type, conference, nick, gMacros.getMacros(param));
	else:
		sendMsg(type, conference, nick, u'нет такого макроса');

def showMacrosList(type, conference, nick, parameters):
	message, disMacroses, macroses = u'', [], [];
	trueJid = getTrueJid(conference, nick);
	isConference = chatInList(conference);
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
		if(type == PUBLIC):
			sendMsg(type, conference, nick, u'ушёл');
		sendMsg(PRIVATE, conference, nick, message);
	else:
		sendMsg(type, conference, nick, u'нету макросов :(');

def showLocalMacroAccess(type, conference, nick, param):
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
					sendMsg(type, conference, nick, u'дала');
				else:
					sendMsg(type, conference, nick, u'ошибочный запрос');
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');
		elif(len(param) == 1):
			access = gMacros.getAccess(macros, conference);
			sendMsg(type, conference, nick, str(access));
		else:
			sendMsg(type, conference, nick, u'ошибочный запрос');
	else:
		sendMsg(type, conference, nick, u'нету такого макроса');
		
def showGlobalMacroAccess(type, conference, nick, param):
	param = param.split();
	macros = param[0];
	if(gMacros.hasMacros(macros)):
		if(len(param) == 2):
			access = param[1];
			if(access.isdigit()):
				access = int(param[1]);
				gMacros.setAccess(macros, access);
				gMacros.saveMacroses();
				sendMsg(type, conference, nick, u'дала');
			else:
				sendMsg(type, conference, nick, u'ошибочный запрос');
		elif(len(param) == 1):
			access = gMacros.getAccess(macros);
			sendMsg(type, conference, nick, str(access));
		else:
			sendMsg(type, conference, nick, u'ошибочный запрос');
	else:
		sendMsg(type, conference, nick, u'нету такого макроса');
			
def loadMacroses(conference):
	gMacros.loadMacroses(conference);

registerPluginHandler(loadMacroses, ADD_CHAT);

def unloadMacroses(conference):
	gMacros.unloadMacroses(conference);

registerPluginHandler(unloadMacroses, DEL_CHAT);
	
def loadGlobalMacroses():
	gMacros.loadMacroses();

registerPluginHandler(loadGlobalMacroses, STARTUP);

registerCommandHandler(delLocalMacros, u'макродел', 20, u'Удалить макроc', u'макродел <название>', (u'макродел глюк', ), CHAT);
registerCommandHandler(delGlobalMacros, u'гмакродел', 100, u'Удалить глобальный макроc', u'ггмакродел <название>', (u'гмакродел глюк', ), ANY | PARAM);

registerCommandHandler(expandLocalMacros, u'макроэксп', 20, u'Развернуть макроc, т.е. посмотреть на него в сыром виде', u'макроэксп <название> [параметры]', (u'макроэксп админ бот', ), CHAT);
registerCommandHandler(expandGlobalMacros, u'гмакроэксп', 100, u'Развернуть макроc, т.е. посмотреть на него в сыром виде', u'гмакроэксп <название> [параметры]', (u'гмакроэксп админ бот', ), ANY | PARAM);

registerCommandHandler(showLocalMacrosInfo, u'макроинфо', 20, u'Открыть макрос, т.е. просто посмотреть как он выглядит', u'макроинфо [название]', (u'макроинфо глюк', ), CHAT);
registerCommandHandler(showGlobalMacrosInfo, u'гмакроинфо', 100, u'Открыть глобальный макрос, т.е. просто посмотреть как он выглядит', u'гмакроинфо [название]', (u'гмакроинфо глюк', ), ANY | PARAM);

registerCommandHandler(showMacrosList, u'макролист', 10, u'Список макросов', None, (u'макролист', ), ANY | NONPARAM);

registerCommandHandler(showLocalMacroAccess, u'макродоступ', 20, u'Изменить или посмотреть доступ к макросу', u'макродоступ <название> [доступ]', (u'макродоступ глюк 10', u'макродоступ глюк'), CHAT);
registerCommandHandler(showGlobalMacroAccess, u'гмакродоступ', 100, u'Изменить или посмотреть доступ к глобальному макросу', u'гмакродоступ <название> [доступ]', (u'гмакродоступ админ 20', u'гмакродоступ админ'), ANY | PARAM);
