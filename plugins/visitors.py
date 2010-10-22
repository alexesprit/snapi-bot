# coding: utf-8

# visitors.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VISITORS_FILE = "visitors.txt"

gVisitors = {}

def saveAutoVisitors(conference):
	fileName = getConfigPath(conference, VISITORS_FILE)
	utils.writeFile(fileName, str(gVisitors[conference]))

def loadAutoVisitors(conference):
	fileName = getConfigPath(conference, VISITORS_FILE)
	utils.createFile(fileName, "[]")
	gVisitors[conference] = eval(utils.readFile(fileName))

def freeAutoVisitors(conference):
	del(gVisitors[conference])

def setAutoVisitor(conference, nick, trueJid, aff, role):
	if(trueJid in gVisitors[conference]):
		setMUCRole(conference, nick, protocol.ROLE_VISITOR, u"автовизитор")

def addAutoVisitor(msgType, conference, nick, param):
	user = param
	setVisitorRole = False
	if(nickInConference(conference, user)):
		trueJid = getTrueJid(conference, user)
		if(getNickKey(conference, user, NICK_HERE)):
			setVisitorRole = True
	elif(param.count("@")):
		trueJid = user
		user = getNickByJid(conference, trueJid)
		if(user):
			setVisitorRole = True
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")
		return
	if(trueJid not in gVisitors[conference]):
		gVisitors[conference].append(trueJid)
		saveAutoVisitors(conference)
		sendMsg(msgType, conference, nick, u"добавила")
		if(setVisitorRole):
			setMUCRole(conference, user, protocol.ROLE_VISITOR)
	else:
		sendMsg(msgType, conference, nick, u"%s уже есть в списке" % (param))

def delAutoVisitort(msgType, conference, nick, param):
	user = param
	setParticipantRole = False
	if(nickInConference(conference, user)):
		trueJid = getTrueJid(conference, user)
		if(getNickKey(conference, user, NICK_HERE)):
			setParticipantRole = True
	elif(param.count("@")):
		trueJid = user
		user = getNickByJid(conference, trueJid)
		if(user):
			setParticipantRole = True
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")
		return
	if(trueJid in gVisitors[conference]):
		gVisitors[conference].remove(trueJid)
		saveAutoVisitors(conference)
		sendMsg(msgType, conference, nick, u"удалила")
		if(setParticipantRole):
			setMUCRole(conference, user, protocol.ROLE_PARTICIPANT)
	else:
		sendMsg(msgType, conference, nick, u"а %s итак нет в списке" % (param))

def showAutoVisitors(msgType, conference, nick, param):
	if(gVisitors[conference]):
		items = [u"%d) %s" % (i + 1, moder) for i, moder in enumerate(gVisitors[conference])]
		message = u"список автомодераторов:\n%s" % ("\n".join(items))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"список автопосетителей пуст")

registerEvent(loadAutoVisitors, ADDCONF)
registerEvent(freeAutoVisitors, DELCONF)
registerJoinHandler(setAutoVisitor)

registerCommand(addAutoVisitor, u"девойс+", 15, 
				u"Добавляет ник или жид в список автопосетителей", 
				u"девойс+ <ник|жид>", 
				(u"девойс+ Nick", u"девойс+ nick@jabber.ru"), 
				CHAT | PARAM)
registerCommand(delAutoVisitort, u"девойс-", 15, 
				u"Удаляет ник или жид из списка автопосетителей", 
				u"девойс- <ник|жид>", 
				(u"девойс- Nick", u"девойс- nick@jabber.ru"), 
				CHAT | PARAM)
registerCommand(showAutoVisitors, u"девойс*", 15, 
				u"Показывает список автопосетителей", 
				None, 
				(u"девойс*", ), 
				CHAT | NONPARAM)
