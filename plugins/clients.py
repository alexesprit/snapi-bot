# coding: utf-8

# clients.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CLIENTS_FILE = "clients.txt"

gUserClients = {}

def loadClientsCache(conference):
	fileName = getConfigPath(conference, CLIENTS_FILE)
	gUserClients[conference] = database.DataBase(fileName)

def freeClientsCache(conference):
	del gUserClients[conference]

def showClients(msgType, conference, nick, param):
	userNick = param or nick
	if nickInConference(conference, userNick):
		trueJid = getTrueJid(conference, userNick)
		if trueJid in gUserClients[conference]:
			clients = gUserClients[conference][trueJid]
			if clients:
				if not param:
					message = u"Ты заходил сюда с "
				else:
					message = param + u" заходил сюда с "
				sendMsg(msgType, conference, nick, message + u", ".join(clients))
			else:
				sendMsg(msgType, conference, nick, u"Нет информации")
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"А это кто?")

def saveUserClient(conference, nick, trueJid, aff, role):
	base = gUserClients[conference]
	if trueJid not in base:
		base[trueJid] = []
	iq = protocol.Iq(protocol.TYPE_GET)
	iq.addChild("query", {}, [], protocol.NS_VERSION)
	iq.setTo(conference + "/" + nick)
	iq.setID(getUniqueID("cli_id"))
	gClient.sendAndCallForResponse(iq, _saveUserClient, (conference, trueJid, ))

def _saveUserClient(stanza, conference, trueJid):
	if protocol.TYPE_RESULT == stanza.getType():
		base = gUserClients[conference]
		for p in stanza.getQueryChildren():
			if p.getName() == "name":
				client = p.getData()
				if not client in base[trueJid]:
					base[trueJid].append(client)

def saveAllClientsBases():
	for conference in getConferences():
		gUserClients[conference].save()

registerEvent(loadClientsCache, ADDCONF)
registerEvent(freeClientsCache, DELCONF)
registerEvent(saveAllClientsBases, SHUTDOWN)

registerJoinHandler(saveUserClient)

registerCommand(showClients, u"клиенты", 10, 
				u"Показывает, с каких клиентов заходил пользователь", 
				u"клиенты [ник]", 
				(u"клиенты", u"клиенты Niсk"), 
				CHAT);
