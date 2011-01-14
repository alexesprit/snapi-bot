# coding: utf-8

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
	rawdata = param.split("=", 1)
	if len(rawdata) != 2:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		macros, body = rawdata
		macros = macros.strip()
		body = body.strip()
		if macros and body:
			if isCommand(macros):
				sendMsg(msgType, conference, nick, u"Это имя уже занято командой")
			elif gMacros.hasMacros(macros):
				sendMsg(msgType, conference, nick, u"Это имя занято глобальным макросом")
			else:
				command = body.split()[0]
				if isCommand(command):
					access = gCommands[command][CMD_ACCESS]
				elif gMacros.hasMacros(command):
					access = gMacros.getAccess(command)
				elif gMacros.hasMacros(command, conference):
					access = gMacros.getAccess(command, conference)
				else:
					sendMsg(msgType, conference, nick, u"Не вижу команду внутри макроса")
					return
				truejid = getTrueJID(conference, nick)
				if access <= getAccess(conference, truejid):
					if gMacros.hasMacros(macros, conference):
						sendMsg(msgType, conference, nick, u"Заменила")
					else:
						sendMsg(msgType, conference, nick, u"Добавила");		
					gMacros.add(macros, body, access, conference)
					gMacros.saveMacroses(conference)
				else:
					sendMsg(msgType, conference, nick, u"Недостаточно прав")
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")

def addGlobalMacros(msgType, conference, nick, param):
	rawdata = param.split("=", 1)
	if len(rawdata) != 2:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		macros, body = rawdata
		macros = macros.strip()
		body = body.strip()
		if macros and body:
			if isCommand(macros):
				sendMsg(msgType, conference, nick, u"Это имя уже занято командой")
			else:
				command = body.split()[0]
				if isCommand(command):
					access = gCommands[command][CMD_ACCESS]
				elif gMacros.hasMacros(command):
					access = gMacros.getAccess(command)
				else:
					sendMsg(msgType, conference, nick, u"Не вижу команду внутри макроса")
					return
				if gMacros.hasMacros(macros):
					access = gMacros.getAccess(macros)
					sendMsg(msgType, conference, nick, u"Заменила")
				else:
					sendMsg(msgType, conference, nick, u"Добавила")
				gMacros.add(macros, body, access)
				gMacros.saveMacroses()
		else:
			sendMsg(msgType, conference, nick, u"Читай справку по команде")

def delLocalMacros(msgType, conference, nick, param):
	if gMacros.hasMacros(param, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if getAccess(conference, truejid) >= access:
			gMacros.remove(param, conference)
			gMacros.saveMacroses(conference)

			sendMsg(msgType, conference, nick, u"Удалила")
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def delGlobalMacros(msgType, conference, nick, param):
	if gMacros.hasMacros(param): 
		gMacros.remove(param)
		gMacros.saveMacroses()

		sendMsg(msgType, conference, nick, u"Удалила")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def expandLocalMacros(msgType, conference, nick, param):
	macros = param.split()[0].lower()
	if gMacros.hasMacros(macros, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if access <= getAccess(conference, truejid):
			sendMsg(msgType, conference, nick, gMacros.expand(param, (conference, nick), conference))
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def expandGlobalMacros(msgType, conference, nick, param):
	macros = param.split()[0].lower()
	if gMacros.hasMacros(macros):
		sendMsg(msgType, conference, nick, gMacros.expand(param, (conference, nick)))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showLocalMacrosInfo(msgType, conference, nick, param):
	if gMacros.hasMacros(param, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if access <= getAccess(conference, truejid):
			sendMsg(msgType, conference, nick, gMacros.getMacros(param, conference))
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showGlobalMacrosInfo(msgType, conference, nick, param):
	param = param.lower()
	if gMacros.hasMacros(param):
		sendMsg(msgType, conference, nick, gMacros.getMacros(param))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showLocalMacroAccess(msgType, conference, nick, param):
	param = param.split(None, 1)
	macros = param[0]
	if gMacros.hasMacros(macros, conference):
		if len(param) == 2:
			access = gMacros.getAccess(macros, conference)
			truejid = getTrueJID(conference, nick)
			if getAccess(conference, truejid) >= access:
				access = param[1]
				if access.isdigit():
					access = int(param[1])
					gMacros.setAccess(macros, access, conference)
					gMacros.saveMacroses(conference)

					sendMsg(msgType, conference, nick, u"Запомнила")
				else:
					sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число больше 0!")
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
		else:
			access = gMacros.getAccess(macros, conference)
			sendMsg(msgType, conference, nick, str(access))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showGlobalMacroAccess(msgType, conference, nick, param):
	param = param.split(None, 1)
	macros = param[0]
	if gMacros.hasMacros(macros):
		if len(param) == 2:
			access = param[1]
			if access.isdigit():
				access = int(param[1])
				gMacros.setAccess(macros, access)
				gMacros.saveMacroses()

				sendMsg(msgType, conference, nick, u"Запомнила")
			else:
				sendMsg(msgType, conference, nick, u"Уровнем доступа должно являться число больше 0!")
		else:
			access = gMacros.getAccess(macros)
			sendMsg(msgType, conference, nick, str(access))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showMacrosList(msgType, conference, nick, parameters):
	macroses, disMacroses = [], []
	buf = []

	isConference = isConferenceInList(conference)
	truejid = getTrueJID(conference, nick)
	access = getAccess(conference, truejid)

	if isConference:
		for macros in gMacros.getMacrosList(conference):
			if isAvailableCommand(conference, macros):
				if gMacros.getAccess(macros, conference) <= access:
					macroses.append(macros)
			else:
				disMacroses.append(macros)
		if macroses:
			macroses.sort()
			buf.append(u"Локальные (%d):\n%s" % (len(macroses), ", ".join(macroses)))
		if disMacroses:
			disMacroses.sort()
			buf.append(u"Отключённые (%d):\n%s" % (len(disMacroses), ", ".join(disMacroses)))

		buf.append("")
		macroses, disMacroses = [], []

	for macros in gMacros.getMacrosList():
		if isConference:
			if isAvailableCommand(conference, macros):
				if gMacros.getAccess(macros) <= access:
					macroses.append(macros)
			else:
				disMacroses.append(macros)
		else:
			access = gMacros.getAccess(macros)
			if access <= getAccess(conference, truejid):
				macroses.append(macros)

	if macroses:
		macroses.sort()
		buf.append(u"Глобальные (%d):\n%s" % (len(macroses), ", ".join(macroses)))
	if isConference:
		if disMacroses:
			disMacroses.sort()
			buf.append(u"Отключённые (%d):\n%s" % (len(disMacroses), ", ".join(disMacroses)))

	if buf:
		if msgType == protocol.TYPE_PUBLIC:
			sendMsg(msgType, conference, nick, u"Ушёл")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, "\n".join(buf))
	else:
		sendMsg(msgType, conference, nick, u"Макросов нет :(")

registerEventHandler(gMacros.loadMacroses, EVT_STARTUP)
registerEventHandler(gMacros.loadMacroses, EVT_ADDCONFERENCE)
registerEventHandler(gMacros.freeMacroses, EVT_DELCONFERENCE)

registerCommand(addLocalMacros, u"макроадд", 20, 
				u"Добавляет локальный макрос", 
				u"<название>=<макрос>",
				(u"глюк = сказать /me подумала, что все глючат", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(addGlobalMacros, u"гмакроадд", 100, 
				u"Добавляет глобальный макрос",
				u"<название> = <макрос>", 
				(u"глюк = сказать /me подумала, что все глючат", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(delLocalMacros, u"макродел", 20, 
				u"Удаляет локальный макроc",
				u"<название>", 
				(u"глюк", ), 
				CMD_CONFERENCE)
registerCommand(delGlobalMacros, u"гмакродел", 100, 
				u"Удаляет глобальный макроc",
				u"<название>", 
				(u"глюк", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(showLocalMacrosInfo, u"макроинфо", 20, 
				u"Показывает локальный макрос в сыром виде",
				u"[название]", 
				(u"глюк", ), 
				CMD_CONFERENCE)
registerCommand(showGlobalMacrosInfo, u"гмакроинфо", 100, 
				u"Показывает глобальный макрос в сыром виде",
				u"[название]", 
				(u"глюк", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(expandLocalMacros, u"макроэксп", 20, 
				u"Разворачивает локальный макрос, используя указанные параметры",
				u"<название> [параметры]", 
				(u"глюк", u"глюк бу!"), 
				CMD_CONFERENCE)
registerCommand(expandGlobalMacros, u"гмакроэксп", 100, 
				u"Разворачивает глобальный макрос, используя указанные параметры",
				u"<название> [параметры]", 
				(u"глюк", u"глюк бу!"), 
				CMD_ANY | CMD_PARAM)
registerCommand(showLocalMacroAccess, u"макродоступ", 20, 
				u"Показывает/изменяет доступ к локальному макросу",
				u"<название> [доступ]", 
				(u"глюк", u"глюк 10"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showGlobalMacroAccess, u"гмакродоступ", 100, 
				u"Показывает/изменяет доступ к глобальному макросу",
				u"<название> [доступ]", 
				(u"админ", u"админ 20"), 
				CMD_ANY | CMD_PARAM)
registerCommand(showMacrosList, u"макролист", 10, 
				u"Показывает список доступных вам макросов",
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
