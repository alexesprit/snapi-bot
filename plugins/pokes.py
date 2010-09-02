# coding: utf-8;

# pokes.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

gPokes = [];

def pokeUser(msgType, conference, nick, param):
	if(msgType == PUBLIC):
		if(param):
			botNick = getBotNick(conference);
			if(param != botNick):
				if(param == u'всех'):
					for userNick in getOnlineNicks(conference):
						if(userNick != botNick and userNick != nick):
							message = random.choice(gPokes);
							sendToConference(conference, u'/me ' + message % (userNick));
				elif(nickIsOnline(conference, param)):
					message = random.choice(gPokes);
					sendToConference(conference, u'/me ' + message % (param));
				else:
					sendMsg(msgType, conference, nick, u'а это кто?');
			else:
				sendMsg(msgType, conference, nick, u'шибко умный, да? ]:->');
		else:
			sendMsg(msgType, conference, nick, u'мазохист? :D');
	else:
		sendMsg(msgType, conference, nick, u':-P');

registerCommand(pokeUser, u'тык', 10, u'Тыкает пользователя. Заставляет его обратить внимание на вас', u'тык <ник>', (u'тык Nick', ), CHAT);

def loadPokes():
	global gPokes;
	gPokes = eval(readFile('resource/pokes.txt', 'utf-8'));

registerEvent(loadPokes, STARTUP);
