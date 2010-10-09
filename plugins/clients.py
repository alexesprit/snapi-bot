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
CLIENTS_ID = "clients_id"

gClients = {}

def loadClientsCache(conference):
	fileName = getConfigPath(conference, CLIENTS_FILE)
	gClients[conference] = database.DataBase(fileName)

def freeClientsCache(conference):
	del(gClients[conference])

def showClients(msgType, conference, nick, param):
	userNick = param or nick
	if(nickInConference(conference, userNick)):
		trueJid = getTrueJid(conference, userNick)
		if(trueJid in gClients[conference]):
			clients = gClients[conference][trueJid]
			if(clients):
				if(not param):
					message = u"ты заходил сюда с "
				else:
					message = param + u" заходил сюда с "
				sendMsg(msgType, conference, nick, message + u", ".join(clients))
			else:
				sendMsg(msgType, conference, nick, u"нет информации")
		else:
			sendMsg(msgType, conference, nick, u"нет информации")
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")

def saveUserClient(conference, nick, trueJid, aff, role):
	base = gClients[conference]
	if(trueJid not in base):
		base[trueJid] = []
	iq = xmpp.Iq(xmpp.TYPE_GET)
	iq.addChild("query", {}, [], xmpp.NS_VERSION)
	iq.setTo(conference + "/" + nick)
	iq.setID(getUniqueID(CLIENTS_ID))
	gClient.SendAndCallForResponse(iq, _saveUserClient, (conference, trueJid, ))

def _saveUserClient(stanza, conference, trueJid):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		base = gClients[conference]
		for p in stanza.getQueryChildren():
			if(p.getName() == "name"):
				client = p.getData()
				if(not client in base[trueJid]):
					base[trueJid].append(client)
					base.save()

registerEvent(loadClientsCache, ADDCONF)
registerEvent(freeClientsCache, DELCONF)

registerJoinHandler(saveUserClient)

registerCommand(showClients, u"клиенты", 10, 
				u"Показывает, с каких клиентов заходил пользователь", 
				u"клиенты [ник]", 
				(u"клиенты", u"клиенты Niсk"), 
				CHAT);
