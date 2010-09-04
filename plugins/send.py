# coding: utf-8;

# send.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Help Copyright (c) 2007 dimichxp <dimichxp@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

SEND_FILE = 'send.txt';

gSend = {};

def addMessageToQueue(msgType, conference, nick, param):
	param = param.split();
	if(len(param) >= 2):
		userNick = param[0];
		message = u'%s попросил меня передать тебе следующее:\n%s' % (nick, ' '.join(param[1:]));
		if(nickIsOnline(conference, userNick)):
			sendMsg(PRIVATE, conference, userNick, message);
			sendMsg(msgType, conference, nick, u'передала');
		elif(nickInConference(conference, userNick)):
			trueJid = getTrueJid(conference, userNick);
			base = gSend[conference];
			messages = base.getKey(trueJid);
			if(not messages):
				messages = [];
			messages.append(message);
			base.setKey(trueJid, messages);
			base.save();
			sendMsg(msgType, conference, nick, u'передам');
		else:
			sendMsg(msgType, conference, nick, u'а это кто?');

registerCommand(addMessageToQueue, u'передать', 10, u'Запоминает сообщение и передаёт его указанному пользователю, как только он зайдёт в конференцию', u'передать <кому> <что>', (u'передать Nick хай!', ), CHAT);

def checkQueue(conference, nick, trueJid, aff, role):
	base = gSend[conference];
	messages = base.getKey(trueJid);
	if(messages):
		for message in messages:
			sendMsg(PRIVATE, conference, nick, message);
			time.sleep(0.5);
		base.delKey(trueJid);
		base.save();

registerJoinHandler(checkQueue);

def loadSendCache(conference):
	fileName = getConfigPath(conference, SEND_FILE);
	gSend[conference] = database.DataBase(fileName);

registerEvent(loadSendCache, ADDCONF);

def unloadSendCache(conference):
	del(gSend[conference]);

registerEvent(unloadSendCache, DELCONF);
