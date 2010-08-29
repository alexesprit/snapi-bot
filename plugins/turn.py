# coding: utf-8;

# turn.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TURN_TIMEOUT = 0.6;

TABLE_RU = u"йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё\"№;:? ";
TABLE_EN = u"qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\ZXCVBNM<>?~@#$^& ";
gTable = dict(zip(TABLE_EN + TABLE_RU, TABLE_RU + TABLE_EN));

gTurnMsgCache = {};

def getChar(char):
	return(gTable.get(char, char));

def turnMessage(text):
	return(''.join(map(getChar, text)));

def turnLastMessage(type, conference, nick, param):
	if(not type == PUBLIC):
		sendMsg(type, conference, nick, u'тока в чате');
		return;
	if(param):
		sendMsg(type, conference, nick, turnMessage(param));
	else:
		trueJid = getTrueJid(conference, nick);
		if(trueJid not in gTurnMsgCache[conference]):
			sendMsg(type, conference, nick, u'а ты ещё ничего не говорил');
		elif(gTurnMsgCache[conference][trueJid].lower() == u'turn'):
			sendMsg(type, conference, nick, u'последнее, что ты сказал, это "turn" :-D');
		else:
			savedMsg = gTurnMsgCache[conference][trueJid];
			receiver = None;
			for userNick in getNicks(conference):
				if(savedMsg.startswith(userNick)):
					for x in [userNick + x for x in (':', ',')]:
						if(savedMsg.startswith(x)):
							savedMsg = savedMsg.replace(x, turnMessage(x));
							receiver = userNick;
				if(receiver):
					break;
			if(receiver):
				sendToConference(conference, u'%s (от %s)' % (turnMessage(savedMsg), nick));
			else:
				sendMsg(type, conference, nick, turnMessage(savedMsg));

registerCommand(turnLastMessage, u'turn', 10, u'Переключает раскладку для последнего сообщения пользователя, вызвавшего команду', u'turn [текст]', (u'turn', u'turn jkjkj'), CHAT);

def saveMessage(stanza, type, conference, nick, trueJid, body):
	if(type == PUBLIC):
		if(trueJid != gJid and trueJid != conference):
			time.sleep(TURN_TIMEOUT);
			gTurnMsgCache[conference][trueJid] = body;

registerMessageHandler(saveMessage, CHAT);

def initTurnCache(conference):
	gTurnMsgCache[conference] = {};

registerEvent(initTurnCache, ADDCONF);
	
def clearTurnCache(conference, nick, trueJid, reason, code):
	if(trueJid in gTurnMsgCache[conference]):
		del(gTurnMsgCache[conference][trueJid]);

registerLeaveHandler(clearTurnCache);
