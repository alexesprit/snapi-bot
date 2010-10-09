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

gUserNotes = {}

def loadUserNotes():
	global gNotes
	gNotes = database.DataBase(getConfigPath(NOTE_FILE))

def addUserNote(msgType, conference, nick, param):
	trueJid = getTrueJid(conference, nick)
	if(trueJid not in gNotes):
		gNotes[trueJid] = []
	text = u"%s\n%s" % (time.strftime("[%d.%m.%y, %H:%M]"), param)
	gNotes[trueJid].append(text)
	gNotes.save()
	sendMsg(msgType, conference, nick, u"записала")

def delUserNote(msgType, conference, nick, param):
	trueJid = getTrueJid(conference, nick)
	if(trueJid in gNotes):
		if(param.isdigit()):
			param = int(param) - 1
			if(param < len(gNotes[trueJid])):
				del(gNotes[trueJid][param])
				if(not gNotes[trueJid]):
					del(gNotes[trueJid])
				gNotes.save()
				sendMsg(msgType, conference, nick, u"удалила")
			else:
				sendMsg(msgType, conference, nick, u"нет такого пункта")
		else:
			sendMsg(msgType, conference, nick, u"читай справку по команде")
	else:
		sendMsg(msgType, conference, nick, u"в твоём блокноте пусто")

def showUserNotes(msgType, conference, nick, param):
	trueJid = getTrueJid(conference, nick)
	if(param == u"сброс"):
		if(trueJid in gNotes):
			del(gNotes[trueJid])
			gNotes.save()
			sendMsg(msgType, conference, nick, u"удалила")
		else:
			sendMsg(msgType, conference, nick, u"а у тебя и так ничего нет :P")
	elif(not param):
		if(trueJid in gNotes):
			message = u"твои заметки:\n"
			items = [u"%d) %s" % (i + 1, x) for i, x in enumerate(gNotes[trueJid])]
			sendMsg(msgType, conference, nick, message + "\n".join(items))
		else:
			sendMsg(msgType, conference, nick, u"в твоём блокноте пусто")

registerEvent(loadUserNotes, STARTUP)

registerCommand(addUserNote, u"заметка+", 10, 
				u"Добавляет запись в ваш блокнот", 
				u"заметка+ <что-то>", 
				(u"заметка+ ы", ), 
				ANY | PARAM)
registerCommand(delUserNote, u"заметка-", 10, 
				u"Удаляет запись из вашего блокнота", 
				u"заметка- <номер>", 
				(u"заметка- 2", ), 
				ANY | PARAM)
registerCommand(showUserNotes, u"заметки", 10, 
				u"Показывает все записи из вашего блокнота. Указав \"сброс\" в кач-ве параметра, вы можете очистить ваши заметки", 
				u"заметки [параметры]", 
				(u"заметки", u"заметки сброс"))
