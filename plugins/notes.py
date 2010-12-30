# coding: utf-8

# notes.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

NOTE_FILE = "notepad.txt"

def loadUserNotes():
	global gUserNotes
	gUserNotes = database.DataBase(getConfigPath(NOTE_FILE))

def addUserNote(msgType, conference, nick, param):
	truejid = getTrueJID(conference, nick)
	if truejid not in gUserNotes:
		gUserNotes[truejid] = []
	text = u"%s\n%s" % (time.strftime("[%d.%m.%y, %H:%M]"), param)
	gUserNotes[truejid].append(text)
	gUserNotes.save()
	sendMsg(msgType, conference, nick, u"Записала")

def delUserNote(msgType, conference, nick, param):
	truejid = getTrueJID(conference, nick)
	if truejid in gUserNotes:
		try:
			param = int(param) - 1
			if param >= 0:
				del gUserNotes[truejid][param]
				if not gUserNotes[truejid]:
					del gUserNotes[truejid]
				gUserNotes.save()
				sendMsg(msgType, conference, nick, u"Удалила")
			else:
				raise IndexError
		except ValueError:
			sendMsg(msgType, conference, nick, u"Для удаления нужно указать номер заметки!")
		except IndexError:
			sendMsg(msgType, conference, nick, u"Нет такой заметки")
	else:
		sendMsg(msgType, conference, nick, u"В твоём блокноте пусто")

def showUserNotes(msgType, conference, nick, param):
	truejid = getTrueJID(conference, nick)
	if param == u"сброс":
		if truejid in gUserNotes:
			del gUserNotes[truejid]
			gUserNotes.save()
			sendMsg(msgType, conference, nick, u"Удалила")
		else:
			sendMsg(msgType, conference, nick, u"А у тебя и так ничего нет :P")
	elif not param:
		if truejid in gUserNotes:
			elements = [u"%d) %s" % (i + 1, note) for i, note in enumerate(gUserNotes[truejid])]
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"Ушли")
			message = u"Твои заметки:\n%s" % ("\n".join(elements))
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"В твоём блокноте пусто")

registerEventHandler(loadUserNotes, EVT_STARTUP)

registerCommand(addUserNote, u"заметка+", 10, 
				u"Добавляет запись в ваш блокнот", 
				u"<что-то>", 
				(u"ы", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(delUserNote, u"заметка-", 10, 
				u"Удаляет запись из вашего блокнота", 
				u"<номер>", 
				(u"2", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(showUserNotes, u"заметки", 10, 
				u"Показывает все записи из вашего блокнота. Указав \"сброс\" в кач-ве параметра, вы можете очистить ваши заметки", 
				u"[параметры]", 
				(None, u"сброс"))
