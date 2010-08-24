# coding: utf-8;

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

CLIENTS_FILE = 'config/%s/clients.txt';
CLIENTS_ID = 'clients_id';

gClientsCache = {};

def showClients(type, conference, nick, param):
	userNick = param or nick;
	if(nickOnlineInChat(conference, userNick)):
		trueJid = getTrueJid(conference, userNick);
		base = gClientsCache[conference];
		if(trueJid in base):
			clients = base.getKey(trueJid);
			if(clients):
				if(not param):
					message = u'ты заходил сюда с ';
				else:
					message = param + u' заходил сюда с ';
				sendMsg(type, conference, nick, message + u', '.join(clients));
			else:
				if(not param):
					sendMsg(type, conference, nick, u'не знаю, с каких клиентов ты заходил');
				else:
					sendMsg(type, conference, nick, u'не знаю, с каких клиентов заходил %s' % param);

def clientsChecking(conference, nick, trueJid, aff, role):
	base = gClientsCache[conference];
	if(trueJid not in base):
		base.setKey(trueJid, []);
	iq = xmpp.Iq('get');
	iq.addChild('query', {}, [], xmpp.NS_VERSION);
	iq.setTo(conference + '/' + nick);
	iq.setID(CLIENTS_ID);
	gClient.SendAndCallForResponse(iq, _clientsChecking, (conference, trueJid, ));

def _clientsChecking(stanza, conference, trueJid):
	if(CLIENTS_ID == stanza.getID()):
		if(stanza.getType() == 'result'):
			base = gClientsCache[conference];
			clients = base.getKey(trueJid);
			for p in stanza.getQueryChildren():
				if(p.getName() == 'name'):
					client = p.getData();
					if(not client in clients):
						clients.append(client);
						base.setKey(trueJid, clients);
						base.save();

def loadClientsCache(conference):
	fileName = CLIENTS_FILE % (conference);
	gClientsCache[conference] = database.DataBase(fileName);

registerPluginHandler(loadClientsCache, ADD_CHAT);
registerJoinHandler(clientsChecking);
registerCommandHandler(showClients, u'клиенты', 10, u'Показывает, с каких клиентов заходил пользователь', u'клиенты [ник]', (u'клиенты', u'клиенты Niсk'), CHAT);
