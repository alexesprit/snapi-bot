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

#TABLE_RU = u",№;:?&йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ";
#TABLE_EN = u"?#$^,?qwertyuiop[]asdfghjkl;'zxcvbnm,.`QWERTYUIOP{}ASDFGHJKL:\ZXCVBNM<>~";

BIG_RU = u'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,?';
BIG_EN = u'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?&';
SML_RU = u"йцукенгшщзхъфывапролджэячсмитьбю.";
SML_EN = u"qwertyuiop[]asdfghjkl;'zxcvbnm,./";

TABLE_BIG = dict(zip(BIG_RU + BIG_EN, BIG_EN + BIG_RU));
TABLE_SML = dict(zip(SML_RU + SML_EN, SML_EN + SML_RU));

gTurnMsgCache = {};

def getBigChar(char):
	return(TABLE_BIG.get(char, char));

def getSmlChar(char):
	return(TABLE_SML.get(char, char));

def turnMessage(text):
	text = ''.join(map(getSmlChar, text));
	text = ''.join(map(getBigChar, text));
	return(text);

def turnLastMessage(msgType, conference, nick, param):
	if(not msgType == PUBLIC):
		sendMsg(msgType, conference, nick, u'тока в чате');
		return;
	if(param):
		sendMsg(msgType, conference, nick, turnMessage(param));
	else:
		trueJid = getTrueJid(conference, nick);
		if(trueJid not in gTurnMsgCache[conference]):
			sendMsg(msgType, conference, nick, u'а ты ещё ничего не говорил');
		elif(gTurnMsgCache[conference][trueJid].lower() == u'turn'):
			sendMsg(msgType, conference, nick, u'последнее, что ты сказал, это "turn" :-D');
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
				sendMsg(msgType, conference, nick, turnMessage(savedMsg));

registerCommand(turnLastMessage, u'turn', 10, u'Переключает раскладку для последнего сообщения пользователя, вызвавшего команду', u'turn [текст]', (u'turn', u'turn jkjkj'), CHAT);

def saveMessage(stanza, msgType, conference, nick, trueJid, body):
	if(msgType == PUBLIC):
		if(trueJid != gJid and trueJid != conference):
			time.sleep(TURN_TIMEOUT);
			gTurnMsgCache[conference][trueJid] = body;

registerMessageHandler(saveMessage, CHAT);

def initTurnCache(conference):
	gTurnMsgCache[conference] = {};

registerEvent(initTurnCache, ADDCONF);

def unloadTurnCache(conference):
	del(gTurnMsgCache[conference]);

registerEvent(unloadTurnCache, DELCONF);

def clearTurnCache(conference, nick, trueJid, reason, code):
	if(trueJid in gTurnMsgCache[conference]):
		del(gTurnMsgCache[conference][trueJid]);

registerLeaveHandler(clearTurnCache);
