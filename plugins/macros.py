# coding: utf-8

# macros.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def addLocalMacros(msgType, conference, nick, param):
	args = param.split("=", 1)
	if len(args) != 2:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		macros, body = args
		macros = macros.strip().lower()
		body = body.strip()
		if macros and body:
			if isCommand(macros):
				sendMsg(msgType, conference, nick, u"Это имя уже занято командой")
			elif gMacros.hasMacros(macros):
				sendMsg(msgType, conference, nick, u"Это имя занято глобальным макросом")
			else:
				command = body.split()[0].lower()
				if isCommand(command):
					access = gCommands[command][CMD_ACCESS]
				else:
					sendMsg(msgType, conference, nick, u"Не вижу команду внутри макроса")
					return
				truejid = getTrueJID(conference, nick)
				if access <= getAccess(conference, truejid):
					if gMacros.hasMacros(macros, conference):
						sendMsg(msgType, conference, nick, u"Заменила")
					else:
						sendMsg(msgType, conference, nick, u"Добавила");		
					gMacros.addMacros(macros, body, access, conference)
					gMacros.saveMacroses(conference)
				else:
					sendMsg(msgType, conference, nick, u"Недостаточно прав")
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")

def addGlobalMacros(msgType, conference, nick, param):
	args = param.split("=", 1)
	if len(args) != 2:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		macros, body = args
		macros = macros.strip().lower()
		body = body.strip()
		if macros and body:
			if isCommand(macros):
				sendMsg(msgType, conference, nick, u"Это имя уже занято командой")
			else:
				command = body.split()[0].lower()
				if isCommand(command):
					access = gCommands[command][CMD_ACCESS]
				else:
					sendMsg(msgType, conference, nick, u"Не вижу команду внутри макроса")
					return
				if gMacros.hasMacros(macros):
					access = gMacros.getAccess(macros)
					sendMsg(msgType, conference, nick, u"Заменила")
				else:
					sendMsg(msgType, conference, nick, u"Добавила")
				gMacros.addMacros(macros, body, access)
				gMacros.saveMacroses()
		else:
			sendMsg(msgType, conference, nick, u"Читай справку по команде")

def delLocalMacros(msgType, conference, nick, param):
	macros = param.lower()
	if gMacros.hasMacros(macros, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if getAccess(conference, truejid) >= access:
			gMacros.delMacros(macros, conference)
			gMacros.saveMacroses(conference)

			sendMsg(msgType, conference, nick, u"Удалила")
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def delGlobalMacros(msgType, conference, nick, param):
	macros = param.lower()
	if gMacros.hasMacros(macros): 
		gMacros.delMacros(macros)
		gMacros.saveMacroses()

		sendMsg(msgType, conference, nick, u"Удалила")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def expandLocalMacros(msgType, conference, nick, param):
	args = param.split(None, 1)
	macros = args[0].lower()
	if gMacros.hasMacros(macros, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if access <= getAccess(conference, truejid):
			if len(args) > 1:
				sendMsg(msgType, conference, nick, 
					gMacros.getParsedMacros(macros, args[1], (conference, nick), conference))
			else:
				sendMsg(msgType, conference, nick, gMacros.getMacros(macros, conference))
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def expandGlobalMacros(msgType, conference, nick, param):
	args = param.split(None, 1)
	macros = args[0].lower()
	if gMacros.hasMacros(macros):
		if len(args) > 1:
			sendMsg(msgType, conference, nick, 
				gMacros.getParsedMacros(macros, args[1], (conference, nick)))
		else:
			sendMsg(msgType, conference, nick, gMacros.getMacros(macros))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showLocalMacrosInfo(msgType, conference, nick, param):
	macros = param.lower()
	if gMacros.hasMacros(macros, conference):
		access = gMacros.getAccess(macros, conference)
		truejid = getTrueJID(conference, nick)
		if access <= getAccess(conference, truejid):
			sendMsg(msgType, conference, nick, gMacros.getMacros(macros, conference))
		else:
			sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showGlobalMacrosInfo(msgType, conference, nick, param):
	macros = param.lower()
	if gMacros.hasMacros(macros):
		sendMsg(msgType, conference, nick, gMacros.getMacros(macros))
	else:
		sendMsg(msgType, conference, nick, u"Нет такого макроса")

def showLocalMacroAccess(msgType, conference, nick, param):
	args = param.split(None, 1)
	macros = args[0].lower()
	if gMacros.hasMacros(macros, conference):
		if len(args) == 2:
			access = gMacros.getAccess(macros, conference)
			truejid = getTrueJID(conference, nick)
			if getAccess(conference, truejid) >= access:
				access = args[1]
				if access.isdigit():
					access = int(args[1])
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
	args = param.split(None, 1)
	macros = args[0].lower()
	if gMacros.hasMacros(macros):
		if len(args) == 2:
			access = args[1]
			if access.isdigit():
				access = int(args[1])
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
			buf.append(u"Локальные (%d): %s\n" % (len(macroses), ", ".join(macroses)))
		if disMacroses:
			disMacroses.sort()
			buf.append(u"Отключённые (%d): %s\n" % (len(disMacroses), ", ".join(disMacroses)))
		buf.append("\n")
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
		buf.append(u"Глобальные (%d): %s\n" % (len(macroses), ", ".join(macroses)))
	if isConference:
		if disMacroses:
			disMacroses.sort()
			buf.append(u"Отключённые (%d): %s\n" % (len(disMacroses), ", ".join(disMacroses)))

	if buf:
		if msgType == protocol.TYPE_PUBLIC:
			sendMsg(msgType, conference, nick, u"Ушёл")
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, "".join(buf))
	else:
		sendMsg(msgType, conference, nick, u"Макросов нет :(")

registerEventHandler(gMacros.loadMacroses, EVT_CONNECTED)
registerEventHandler(gMacros.loadMacroses, EVT_ADDCONFERENCE)
registerEventHandler(gMacros.freeMacroses, EVT_DELCONFERENCE)

registerCommand(addLocalMacros, u"макроадд", 20, 
				u"Добавляет локальный макрос", 
				u"<название> = <макрос>",
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
				u"<название>", 
				(u"глюк", ), 
				CMD_CONFERENCE)
registerCommand(showGlobalMacrosInfo, u"гмакроинфо", 100, 
				u"Показывает глобальный макрос в сыром виде",
				u"<название>", 
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
				CMD_ANY | CMD_NONPARAM | CMD_FROZEN)
