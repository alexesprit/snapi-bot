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
	trueJid = getTrueJid(conference, nick)
	if trueJid not in gUserNotes:
		gUserNotes[trueJid] = []
	text = u"%s\n%s" % (time.strftime("[%d.%m.%y, %H:%M]"), param)
	gUserNotes[trueJid].append(text)
	gUserNotes.save()
	sendMsg(msgType, conference, nick, u"Записала")

def delUserNote(msgType, conference, nick, param):
	trueJid = getTrueJid(conference, nick)
	if trueJid in gUserNotes:
		if param.isdigit():
			param = int(param) - 1
			if param < len(gUserNotes[trueJid]):
				del gUserNotes[trueJid][param]
				if not gUserNotes[trueJid]:
					del gUserNotes[trueJid]
				gUserNotes.save()
				sendMsg(msgType, conference, nick, u"Удалила")
			else:
				sendMsg(msgType, conference, nick, u"Нет такой заметки")
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"В твоём блокноте пусто")

def showUserNotes(msgType, conference, nick, param):
	trueJid = getTrueJid(conference, nick)
	if param == u"сброс":
		if trueJid in gUserNotes:
			del gUserNotes[trueJid]
			gUserNotes.save()
			sendMsg(msgType, conference, nick, u"Удалила")
		else:
			sendMsg(msgType, conference, nick, u"А у тебя и так ничего нет :P")
	elif not param:
		if trueJid in gUserNotes:
			message = u"Твои заметки:\n"
			items = [u"%d) %s" % (i + 1, x) for i, x in enumerate(gUserNotes[trueJid])]
			sendMsg(msgType, conference, nick, message + "\n".join(items))
		else:
			sendMsg(msgType, conference, nick, u"В твоём блокноте пусто")

registerEvent(loadUserNotes, EVT_STARTUP)

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
