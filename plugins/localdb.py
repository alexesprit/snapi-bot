# coding: utf-8

# localdb.py 
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

LOCALDB_FILE = "localdb.txt"

gLocalBase = {}

def getLocalKeyToPublic(msgType, conference, nick, param):
	param = param.lower()
	if(param in gLocalBase[conference]):
		sendMsg(msgType, conference, nick, u"про %s я знаю следующее:\n%s" % (param, gLocalBase[conference][param]))
	else:	
		sendMsg(msgType, conference, nick, u"я хз что такое %s :(" % (param))

def getLocalKeyToPrivate(msgType, conference, nick, param):
	param = param.split()
	confJid = ""
	if(len(param) == 2):
		userNick = param[0].strip()
		if(nickIsOnline(conference, userNick)):
			confJid = conference + "/" + userNick
			key = param[1].lower()
	elif(len(param) == 1):
		confJid = conference + "/" + nick
		key = param[0].lower()
	if(confJid):
		if(key in gLocalBase[conference]):
			if(xmpp.TYPE_PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u"ушло")
			sendTo(xmpp.TYPE_PRIVATE, confJid, u"про %s я знаю следующее:\n%s" % (key, gLocalBase[conference][key]))
		else:
			sendMsg(msgType, conference, nick, u"я хз что такое %s :(" % key)
	else:
		sendMsg(msgType, conference, nick, u"кому?")

def setLocalKey(msgType, conference, nick, param):
	param = param.split("=", 1)
	if(len(param) == 2):
		key = param[0].lower().strip()
		value = param[1].strip()
		if(value):
			gLocalBase[conference][key] = u"%s (от %s)" % (value, nick)
			saveLocalBase(conference)
			sendMsg(msgType, conference, nick, u"буду знать, что такое %s" % (key))
		else:
			if(key in gLocalBase[conference]):
				del(gLocalBase[conference][key])
				saveLocalBase(conference)
				sendMsg(msgType, conference, nick, u"прибила %s нафиг" % (key))
			else:
				sendMsg(msgType, conference, nick, u"%s и так нету :-P" % (key))
	else:
		sendMsg(msgType, conference, nick, u"читай справку по команде")

def searchLocalKey(msgType, conference, nick, param):
	foundItems = []
	for key in gLocalBase[conference].keys():
		if(key.count(param)):
			foundItems.append(key)
	if(foundItems):
		sendMsg(msgType, conference, nick, u"совпало с %s" % (", ".join(foundItems)))
	else:
		sendMsg(msgType, conference, nick, u"ни с чем не совпало :(")

def showAllLocalKeys(msgType, conference, nick, parameters):
	if(gLocalBase[conference]):
		sendMsg(msgType, conference, nick, ", ".join(sorted(gLocalBase[conference].keys())))
	else:
		sendMsg(msgType, conference, nick, "база пуста!")

def loadLocalBase(conference):
	fileName = getConfigPath(conference, LOCALDB_FILE)
	util.createFile(fileName, "{}")
	gLocalBase[conference] = eval(util.readFile(fileName))

def saveLocalBase(conference):
	fileName = getConfigPath(conference, LOCALDB_FILE)
	util.writeFile(fileName, str(gLocalBase[conference]))

def freeLocalBase(conference):
	del(gLocalBase[conference])

registerEvent(loadLocalBase, ADDCONF)
registerEvent(freeLocalBase, DELCONF)

registerCommand(getLocalKeyToPublic, u"???", 10, 
				u"Ищет ответ на вопрос в локальной базе", 
				u"??? <запрос>", 
				(u"??? что-то", u"??? что-то ещё"), 
				CHAT | PARAM)
registerCommand(getLocalKeyToPrivate, u"!??", 10, 
				u"Ищет ответ на вопрос в локальной базе и посылает его в приват", 
				u"!?? [ник] <запрос>", 
				(u"!?? что-то", u"!?? guy что-то"), 
				CHAT | PARAM)
registerCommand(setLocalKey, u"!!!", 20, 
				u"Устанавливает ответ на вопрос в локальной базе", 
				u"!!! <запрос> = <ответ>", 
				(u"!!! что-то = the best!", u"!!! что-то ="), 
				CHAT | PARAM)
registerCommand(searchLocalKey, u"???поиск", 10, 
				u"Поиск по базе", 
				u"???поиск <запрос>", 
				(u"???поиск что-то", ), 
				CHAT | PARAM)
registerCommand(showAllLocalKeys, u"???все", 10, 
				u"Показывает все ключи базы", 
				None, 
				(u"???все", ), 
				CHAT | NONPARAM)
